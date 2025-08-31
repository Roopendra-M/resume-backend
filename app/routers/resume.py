# app/routers/resume.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime
from typing import Optional, List
from app.db import db
from app.models import ResumeUploadOut
from app.security import get_current_user
from app.utils import extract_text_from_pdf, extract_text_from_docx, resume_jd_similarity

router = APIRouter(prefix="/api/resume", tags=["Resume"])

@router.post("/upload", response_model=ResumeUploadOut)
async def upload_resume(
    file: UploadFile = File(...),
    job_descriptions: Optional[List[str]] = Form(None),
    authed=Depends(get_current_user)
):
    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(content)
    elif file.filename.lower().endswith(".docx"):
        resume_text = extract_text_from_docx(content)
    else:
        raise HTTPException(400, "Unsupported file type")

    similarities = {}
    if job_descriptions:
        for jd in job_descriptions:
            result = await resume_jd_similarity(resume_text, jd)
            similarities[jd] = result.get("similarity_score", 0)

    doc = {
        "user_id": authed["user_id"],
        "filename": file.filename,
        "text": resume_text,
        "uploaded_at": datetime.utcnow()
    }
    res = await db.resumes.insert_one(doc)
    excerpt = (resume_text[:300] + "...") if len(resume_text) > 303 else resume_text

    return ResumeUploadOut(
        id=str(res.inserted_id),
        filename=file.filename,
        text_excerpt=excerpt,
        uploaded_at=doc["uploaded_at"],
        similarity_score=similarities
    )

@router.get("/me", response_model=List[ResumeUploadOut])
async def my_resumes(authed=Depends(get_current_user)):
    cur = db.resumes.find({"user_id": authed["user_id"]}).sort("uploaded_at", -1)
    out = []
    async for r in cur:
        excerpt = (r.get("text", "")[:300] + "...") if len(r.get("text", "")) > 303 else r.get("text", "")
        out.append(
            ResumeUploadOut(
                id=str(r["_id"]),
                filename=r.get("filename", "Unknown"),
                text_excerpt=excerpt,
                uploaded_at=r.get("uploaded_at", datetime.utcnow()),
                similarity_score=r.get("similarity_score", {})
            )
        )
    return out
