# app/models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal, Dict
from datetime import datetime

Role = Literal["user", "admin"]

# ---------------- User models ----------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role

# ---------------- Job models ----------------
class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    skills: List[str]

class JobOut(JobCreate):
    id: str
    created_at: datetime

# ---------------- Resume models ----------------
class ResumeUploadOut(BaseModel):
    id: str
    filename: str
    text_excerpt: str
    uploaded_at: datetime
    similarity_score: Dict[str, float]  # JD -> similarity %

# ---------------- Application models ----------------
class ApplyIn(BaseModel):
    job_id: str
    resume_id: Optional[str] = None

class ApplicationOut(BaseModel):
    id: str
    job_id: str
    job_title: str
    company: str
    location: str
    match_score: float
    created_at: datetime

# ---------------- Feedback models ----------------
class FeedbackIn(BaseModel):
    message: str
    rating: int = Field(ge=1, le=5)

class FeedbackOut(BaseModel):
    id: str
    user_id: str
    message: str
    rating: int
    created_at: datetime

# ---------------- Chat model ----------------
class ChatQuery(BaseModel):
    query: str
