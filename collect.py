from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Content
from services.parser import fetch_url_content
from services.llm import analyze_content

router = APIRouter(prefix="/api", tags=["collect"])


class CollectRequest(BaseModel):
    url: str
    user_id: str = "anonymous"


class CollectResponse(BaseModel):
    id: str
    title: str
    summary: str
    main_content: str
    key_points: list
    notes: list
    value: str
    tags: list


@router.post("/collect")
def collect_url(request: CollectRequest, db: Session = Depends(get_db)):
    result = fetch_url_content(request.url)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=f"无法抓取网页: {result.get('error', '未知错误')}")

    analysis = analyze_content(result["title"], result["content"])

    content = Content(
        url=request.url,
        title=result["title"],
        content=result["content"],
        summary=analysis.get("summary", ""),
        main_content=analysis.get("main_content", ""),
        key_points=analysis.get("key_points", []),
        notes=analysis.get("notes", []),
        value=analysis.get("value", ""),
        tags=analysis.get("tags", []),
        user_id=request.user_id
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return {
        "success": True,
        "data": {
            "id": content.id,
            "title": content.title,
            "summary": content.summary,
            "main_content": content.main_content,
            "key_points": content.key_points,
            "notes": content.notes,
            "value": content.value,
            "tags": content.tags
        }
    }


@router.get("/contents")
def list_contents(user_id: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(Content)
    if user_id:
        query = query.filter(Content.user_id == user_id)

    contents = query.order_by(Content.created_at.desc()).all()

    return {
        "success": True,
        "data": {
            "contents": [c.to_dict() for c in contents]
        }
    }


@router.delete("/contents/{content_id}")
def delete_content(content_id: str, user_id: str = "anonymous", db: Session = Depends(get_db)):
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == user_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    db.delete(content)
    db.commit()

    return {"success": True}
