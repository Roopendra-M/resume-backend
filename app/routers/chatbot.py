from fastapi import APIRouter, Depends
from app.models import ChatQuery
from app.security import require_role
from app.db import db

router = APIRouter(prefix="/api/chatbot",tags=["Chatbot"])

@router.post("/", response_model=dict)
async def query_candidates(payload: ChatQuery, authed=Depends(require_role(["admin"]))):
    q = payload.query.lower()
    if "top python" in q:
        cur = db.resumes.find({"skills": "python"}).limit(10)
        items = []
        async for r in cur:
            items.append({"user_id": r["user_id"], "skills": r.get("skills", [])})
        return {"answer": f"Found {len(items)} candidates mentioning Python", "items": items}
    return {"answer": "Query not recognized in demo. Try: 'Top Python skill candidates'.", "items": []}
