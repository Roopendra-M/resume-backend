
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.db import db
from app.models import FeedbackIn, FeedbackOut
from app.security import get_current_user, require_role

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("/", response_model=dict)
async def submit_feedback(payload: FeedbackIn, authed=Depends(get_current_user)):
    doc = {
        "user_id": authed["user_id"],
        "message": payload.message,
        "rating": int(payload.rating),
        "created_at": datetime.utcnow()
    }
    res = await db.feedback.insert_one(doc)
    return {"ok": True, "id": str(res.inserted_id)}

@router.get("/", response_model=list[FeedbackOut])
async def list_feedback(authed=Depends(lambda: require_role(["admin"]))):
    cur = db.feedback.find().sort("created_at",-1).limit(200)
    out = []
    async for f in cur:
        out.append(FeedbackOut(id=str(f["_id"]), user_id=f["user_id"], message=f["message"], rating=f["rating"], created_at=f["created_at"]))
    return out

@router.get("/stats", response_model=dict)
async def feedback_stats(authed=Depends(lambda: require_role(["admin"]))):
    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}]
    cur = db.feedback.aggregate(pipeline)
    stats = await cur.to_list(length=1)
    if not stats:
        return {"avg": 0, "count": 0}
    s = stats[0]
    return {"avg": round(s.get("avg",0),2), "count": s.get("count",0)}
