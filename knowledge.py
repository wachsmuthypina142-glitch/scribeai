from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from database import get_db, Content, Category, Relation
from services.llm import analyze_paper
from services.pdf_parser import parse_pdf
import os
import uuid
import shutil

router = APIRouter(prefix="/api", tags=["knowledge"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


# ============ 分类管理 ============

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[str] = None
    color: Optional[str] = None


@router.post("/categories")
def create_category(request: CategoryCreate, user_id: str = "anonymous", db: Session = Depends(get_db)):
    category = Category(
        name=request.name,
        parent_id=request.parent_id,
        color=request.color,
        user_id=user_id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"success": True, "data": category.to_dict()}


@router.get("/categories")
def list_categories(user_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Category)
    if user_id:
        query = query.filter(Category.user_id == user_id)

    categories = query.order_by(Category.created_at.desc()).all()
    return {"success": True, "data": {"categories": [c.to_dict() for c in categories]}}


@router.put("/categories/{category_id}")
def update_category(category_id: str, request: CategoryUpdate, user_id: str = "anonymous", db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if request.name is not None:
        category.name = request.name
    if request.parent_id is not None:
        category.parent_id = request.parent_id
    if request.color is not None:
        category.color = request.color

    db.commit()
    db.refresh(category)
    return {"success": True, "data": category.to_dict()}


@router.delete("/categories/{category_id}")
def delete_category(category_id: str, user_id: str = "anonymous", db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db.query(Content).filter(Content.category_id == category_id).update({"category_id": None})
    db.delete(category)
    db.commit()
    return {"success": True}


# ============ 内容分类 ============

@router.post("/contents/{content_id}/category")
def set_content_category(content_id: str, category_id: Optional[str] = None, user_id: str = "anonymous", db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id, Content.user_id == user_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    content.category_id = category_id
    db.commit()
    return {"success": True, "data": content.to_dict()}


# ============ 文件上传 ============

class FileCollectRequest(BaseModel):
    title: str
    file_path: str
    file_type: str = "pdf"
    user_id: str = "anonymous"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = "anonymous"):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="仅支持 PDF、TXT、MD 文件")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "data": {
            "file_id": file_id,
            "file_path": file_path,
            "file_name": file.filename,
            "file_type": file_ext[1:]
        }
    }


@router.post("/collect-file")
def collect_file(request: FileCollectRequest, db: Session = Depends(get_db)):
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=400, detail="文件不存在")

    file_ext = os.path.splitext(request.file_path)[1].lower()

    if file_ext == ".pdf":
        result = parse_pdf(request.file_path)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "PDF 解析失败"))

        analysis = analyze_paper(result["title"], result["preview"] or result["content"])

        content = Content(
            url=f"file://{request.file_path}",
            title=result["title"],
            content=result["content"][:8000],
            summary=analysis.get("summary", ""),
            main_content=analysis.get("main_content", ""),
            key_points=analysis.get("key_points", []),
            notes=analysis.get("notes", []),
            value=analysis.get("value", ""),
            tags=analysis.get("tags", []),
            file_path=request.file_path,
            file_type="pdf",
            entities=analysis.get("entities", {}),
            user_id=request.user_id
        )
    else:
        with open(request.file_path, "r", encoding="utf-8") as f:
            text_content = f.read()

        content = Content(
            url=f"file://{request.file_path}",
            title=request.title or os.path.basename(request.file_path),
            content=text_content[:8000],
            file_path=request.file_path,
            file_type=file_ext[1:],
            user_id=request.user_id
        )

    db.add(content)
    db.commit()
    db.refresh(content)

    return {
        "success": True,
        "data": content.to_dict()
    }


# ============ 关联关系 ============

class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = "related"
    note: Optional[str] = None


@router.post("/relations")
def create_relation(request: RelationCreate, user_id: str = "anonymous", db: Session = Depends(get_db)):
    source = db.query(Content).filter(Content.id == request.source_id, Content.user_id == user_id).first()
    target = db.query(Content).filter(Content.id == request.target_id, Content.user_id == user_id).first()

    if not source or not target:
        raise HTTPException(status_code=404, detail="源或目标内容不存在")

    relation = Relation(
        source_id=request.source_id,
        target_id=request.target_id,
        relation_type=request.relation_type,
        note=request.note,
        user_id=user_id
    )
    db.add(relation)
    db.commit()
    db.refresh(relation)

    return {"success": True, "data": relation.to_dict()}


@router.get("/relations")
def list_relations(user_id: str = Query(None), content_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Relation)
    if user_id:
        query = query.filter(Relation.user_id == user_id)
    if content_id:
        query = query.filter((Relation.source_id == content_id) | (Relation.target_id == content_id))

    relations = query.all()
    return {
        "success": True,
        "data": {
            "relations": [r.to_dict() for r in relations]
        }
    }


@router.delete("/relations/{relation_id}")
def delete_relation(relation_id: str, user_id: str = "anonymous", db: Session = Depends(get_db)):
    relation = db.query(Relation).filter(Relation.id == relation_id, Relation.user_id == user_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="关系不存在")

    db.delete(relation)
    db.commit()
    return {"success": True}


# ============ 知识图谱 ============

@router.get("/graph")
def get_graph(user_id: str = Query(None), db: Session = Depends(get_db)):
    content_query = db.query(Content)
    if user_id:
        content_query = content_query.filter(Content.user_id == user_id)

    contents = content_query.all()

    nodes = []
    tag_nodes = set()
    entity_map = {}

    for content in contents:
        node = {
            "id": content.id,
            "title": content.title,
            "type": content.file_type if content.file_type != "url" else "web",
            "category_id": content.category_id,
            "tags": content.tags or [],
            "url": content.url
        }
        nodes.append(node)

        for tag in (content.tags or []):
            tag_nodes.add(tag)

        for entity_key, entity_value in (content.entities or {}).items():
            if isinstance(entity_value, list):
                for e in entity_value:
                    entity_map[f"{entity_key}:{e}"] = {"type": entity_key, "name": e}

    for tag in tag_nodes:
        nodes.append({
            "id": f"tag_{tag}",
            "title": tag,
            "type": "tag"
        })

    for entity_key, entity in entity_map.items():
        nodes.append({
            "id": f"entity_{entity_key}",
            "title": entity["name"],
            "type": "entity",
            "entity_type": entity["type"]
        })

    relation_query = db.query(Relation)
    if user_id:
        relation_query = relation_query.filter(Relation.user_id == user_id)

    relations = relation_query.all()
    edges = []

    for rel in relations:
        edges.append({
            "source": rel.source_id,
            "target": rel.target_id,
            "relation": rel.relation_type,
            "id": rel.id
        })

    for content in contents:
        for tag in (content.tags or []):
            edges.append({
                "source": content.id,
                "target": f"tag_{tag}",
                "relation": "tagged",
                "id": f"edge_{content.id}_{tag}"
            })

    return {
        "success": True,
        "data": {
            "nodes": nodes,
            "edges": edges
        }
    }


# ============ 原有 API 兼容 ============

@router.get("/knowledge/tags")
def get_tags(user_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Content)
    if user_id:
        query = query.filter(Content.user_id == user_id)
    contents = query.all()

    tag_counts = {}
    for content in contents:
        for tag in content.tags or []:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    tags = [{"name": name, "count": count} for name, count in sorted(
        tag_counts.items(), key=lambda x: x[1], reverse=True
    )]

    return {"success": True, "data": {"tags": tags}}


@router.get("/knowledge/by-tag")
def get_by_tag(tag: str = Query(...), user_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Content).filter(Content.tags.contains(tag))
    if user_id:
        query = query.filter(Content.user_id == user_id)

    contents = query.order_by(Content.created_at.desc()).all()
    return {"success": True, "data": {"contents": [c.to_dict() for c in contents]}}


@router.get("/knowledge/stats")
def get_stats(user_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Content)
    if user_id:
        query = query.filter(Content.user_id == user_id)

    total = query.count()
    contents = query.all()

    tag_counts = {}
    for content in contents:
        for tag in content.tags or []:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "success": True,
        "data": {
            "total": total,
            "tag_count": len(tag_counts),
            "top_tags": [{"name": name, "count": count} for name, count in list(
                sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            )[:5]]
        }
    }
