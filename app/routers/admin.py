
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.db import db
from app.security import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard", response_model=dict)
async def dashboard(authed=Depends(lambda: require_role(["admin"]))):
    users = await db.users.count_documents({})
    jobs = await db.jobs.count_documents({})
    resumes = await db.resumes.count_documents({})
    apps = await db.applications.count_documents({})
    # Simple 30-day stats
    since = datetime.utcnow() - timedelta(days=30)
    apps_last_30 = await db.applications.count_documents({"created_at": {"$gte": since}})
    return {
        "users": users,
        "jobs": jobs,
        "resumes": resumes,
        "applications": apps,
        "applications_last_30": apps_last_30
    }
