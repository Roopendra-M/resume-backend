from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from app.db import db
from app.models import UserCreate, UserLogin, Token, UserPublic
from app.security import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth",tags=["Auth"])

@router.post("/signup", response_model=UserPublic)
async def signup(payload: UserCreate):
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "email": payload.email.lower(),
        "password": hash_password(payload.password),
        "name": payload.name,
        "role": "user",
        "created_at": datetime.utcnow(),
    }
    res = await db.users.insert_one(user)
    return UserPublic(id=str(res.inserted_id), email=user["email"], name=user["name"], role="user")

@router.post("/login", response_model=Token)
async def login(payload: UserLogin):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"user_id": str(user["_id"]), "email": user["email"], "role": user.get("role", "user")})
    return Token(access_token=token, role=user.get("role", "user"))

@router.post("/admin/login", response_model=Token)
async def admin_login(payload: UserLogin):
    admin = await db.users.find_one({"email": settings.ADMIN_EMAIL.lower(), "role": "admin"})
    if not admin:
        res = await db.users.insert_one({
            "email": settings.ADMIN_EMAIL.lower(),
            "password": hash_password(settings.ADMIN_PASSWORD),
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        admin_id = str(res.inserted_id)
        admin_hashed_pw = hash_password(settings.ADMIN_PASSWORD)
    else:
        admin_id = str(admin["_id"])
        admin_hashed_pw = admin["password"]

    if payload.email.lower() != settings.ADMIN_EMAIL.lower() or not verify_password(payload.password, admin_hashed_pw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")

    token = create_access_token({"user_id": admin_id, "email": settings.ADMIN_EMAIL.lower(), "role": "admin"})
    return Token(access_token=token, role="admin")

@router.get("/me", response_model=UserPublic)
async def me(authed=Depends(get_current_user)):
    u = await db.users.find_one({"_id": ObjectId(authed["user_id"])})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic(id=str(u["_id"]), email=u["email"], name=u["name"], role=u.get("role", "user"))
