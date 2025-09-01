from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    JWT_SECRET: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ALLOW_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,https://resume-frontend-cyan.vercel.app/"
    HUGGINGFACE_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

settings = Settings()

ALLOWED_ORIGINS: List[str] = [
    o.strip() for o in settings.ALLOW_ORIGINS.split(",") if o.strip()
]
