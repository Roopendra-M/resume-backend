# app/routers/apply.py
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.db import db
from app.models import ApplyIn, ApplicationOut
from app.security import get_current_user
import re

router = APIRouter(prefix="/api/apply", tags=["Apply"])

# Simple skill match based on resume text words & job description words
async def match_score_hf(resume_text: str, job_description: str) -> float:
    def clean_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)

    r_words = set(resume_clean.split())
    j_words = set(job_clean.split())

    inter = len(r_words & j_words)
    return round(100.0 * inter / max(1, len(j_words)), 2)

@router.post("/", response_model=ApplicationOut)
async def apply_job(payload: ApplyIn, authed=Depends(get_current_user)):
    job = await db.jobs.find_one({"_id": ObjectId(payload.job_id)})
    if not job:
        raise HTTPException(404, "Job not found")

    resume = None
    if payload.resume_id:
        resume = await db.resumes.find_one({"_id": ObjectId(payload.resume_id), "user_id": authed["user_id"]})
    else:
        resume = await db.resumes.find_one({"user_id": authed["user_id"]}, sort=[("uploaded_at", -1)])

    if not resume:
        raise HTTPException(400, "Upload a resume first")

    score = await match_score_hf(resume.get("text", ""), job.get("description", ""))

    doc = {
        "user_id": authed["user_id"],
        "job_id": str(job["_id"]),
        "match_score": score,
        "created_at": datetime.utcnow(),
    }
    res = await db.applications.insert_one(doc)

    return ApplicationOut(
        id=str(res.inserted_id),
        job_id=str(job["_id"]),
        job_title=job.get("title", "Unknown"),
        company=job.get("company", "Unknown"),
        location=job.get("location", "Unknown"),
        match_score=score,
        created_at=doc["created_at"]
    )

@router.get("/me", response_model=list[ApplicationOut])
async def my_applications(authed=Depends(get_current_user)):
    cur = db.applications.find({"user_id": authed["user_id"]}).sort("created_at", -1)
    out = []
    async for a in cur:
        job = await db.jobs.find_one({"_id": ObjectId(a["job_id"])})
        out.append(
            ApplicationOut(
                id=str(a["_id"]),
                job_id=a["job_id"],
                job_title=job.get("title", "Unknown") if job else "Unknown",
                company=job.get("company", "Unknown") if job else "Unknown",
                location=job.get("location", "Unknown") if job else "Unknown",
                match_score=a.get("match_score", 0),
                created_at=a.get("created_at", datetime.utcnow())
            )
        )
    return out
