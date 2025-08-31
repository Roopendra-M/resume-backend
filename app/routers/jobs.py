# app/routers/jobs.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.db import db
from app.security import require_role

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    skills: List[str]

@router.post("/", response_model=dict)
async def create_job(payload: JobCreate, user: dict = Depends(require_role(["admin"]))):
    new_job = {
        "title": payload.title,
        "company": payload.company,
        "location": payload.location,
        "description": payload.description,
        "skills": payload.skills,
        "created_at": datetime.utcnow(),
        "created_by": user["user_id"],
    }
    result = await db.jobs.insert_one(new_job)
    return {
        "id": str(result.inserted_id),
        "title": new_job.get("title", "Unknown"),
        "company": new_job.get("company", "Unknown"),
        "location": new_job.get("location", "Unknown"),
        "description": new_job.get("description", ""),
        "skills": new_job.get("skills", []),
        "created_at": new_job.get("created_at"),
        "created_by": new_job.get("created_by"),
    }

@router.get("/", response_model=List[dict])
async def list_jobs():
    docs = await db.jobs.find().sort("created_at", -1).to_list(100)
    out = []
    for j in docs:
        out.append({
            "id": str(j.get("_id")),
            "title": j.get("title", "Unknown"),
            "company": j.get("company", "Unknown"),
            "location": j.get("location", "Unknown"),
            "description": j.get("description", ""),
            "skills": j.get("skills", []),
            "created_at": j.get("created_at"),
        })
    return out
