# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import asyncio

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def init_db():
    async def create_indexes():
        await db.users.create_index("email", unique=True)
        await db.jobs.create_index([("created_at", -1)])  # Ensure created_at is indexed
        await db.applications.create_index([("user_id", 1), ("job_id", 1)], unique=False)
    asyncio.create_task(create_indexes())

async def close_db():
    client.close()
