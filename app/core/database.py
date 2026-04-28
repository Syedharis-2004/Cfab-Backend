from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
import logging

logger = logging.getLogger(__name__)

# List of all Beanie document models for initialization
from app.models.user import User
from app.models.assignment import Assignment
from app.models.coding_assignment import CodingAssignment
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.models.test_case import TestCase
from app.models.submission import Submission

_db_initialized = False

async def init_db():
    global _db_initialized
    if _db_initialized:
        return

    try:
        if not settings.MONGODB_URL:
            raise ValueError("MONGODB_URL is missing. Please set MONGODB_URL or DATABASE_URL in environment variables.")

        # Use a slightly longer timeout for Vercel cold starts
        client = AsyncIOMotorClient(
            settings.MONGODB_URL, 
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
        
        # Extract db name from URL or use default
        try:
            db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
        except:
            db_name = "check_yourself"
        
        await init_beanie(
            database=client[db_name],
            document_models=[
                User,
                Assignment,
                CodingAssignment,
                Quiz,
                QuizQuestion,
                UserAnswer,
                TestCase,
                Submission,
            ]
        )
        _db_initialized = True
        logger.info(f"Beanie initialized successfully for database '{db_name}'.")
    except Exception as e:
        logger.error(f"CRITICAL: Database initialization failed: {str(e)}")
        # On Vercel, it's better to let it fail so we can catch it in middleware
        _db_initialized = False
        raise e
