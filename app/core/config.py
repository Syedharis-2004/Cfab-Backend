import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 30)
    
    # Allow DATABASE_URL as a fallback for MONGODB_URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    MONGODB_URL: str = os.getenv("MONGODB_URL") or os.getenv("DATABASE_URL") or ""
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    UPLOAD_DIR: str = "uploads/assignments"

settings = Settings()
