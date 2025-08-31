from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db, close_db
from app.routers import auth, jobs, resume, apply, feedback, admin, chatbot
from app.config import ALLOWED_ORIGINS
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Resume Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db()

# Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resume.router)
app.include_router(apply.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(chatbot.router)

@app.get("/api/health")
async def health():
    return {"ok": True}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response
