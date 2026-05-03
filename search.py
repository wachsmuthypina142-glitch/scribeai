from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Content
from services.llm import answer_question
import re

router = APIRouter(prefix="/api", tags=["search"])


class AskRequest(BaseModel):
    question: str
    user_id: str = "anonymous"


@router.post("/ask")
def ask(request: AskRequest, db: Session = Depends(get_db)):
    contents = db.query(Content).filter(
        Content.user_id == request.user_id
    ).all()

    if not contents:
        return {
            "success": True,
            "data": {
                "answer": "知识库为空，请先收藏一些内容。",
                "sources": []
            }
        }

    context = [
        {"title": c.title, "url": c.url, "summary": c.summary, "content": c.content}
        for c in contents
    ]

    result = answer_question(request.question, context)

    return {
        "success": True,
        "data": result
    }


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    user_id: str = Query("anonymous"),
    db: Session = Depends(get_db)
):
    contents = db.query(Content).filter(
        Content.user_id == user_id
    ).all()

    q_lower = q.lower()
    results = []

    for content in contents:
        if (q_lower in (content.title or "").lower() or
            q_lower in (content.summary or "").lower() or
            q_lower in (content.content or "").lower() or
            any(q_lower in tag.lower() for tag in (content.tags or []))):
            results.append(content.to_dict())

    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {
        "success": True,
        "data": {
            "query": q,
            "total": len(results),
            "results": results[:20]
        }
    }
