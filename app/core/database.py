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

async def init_db():
    try:
        if not settings.MONGODB_URL:
            logger.error("MONGODB_URL is not set in environment variables.")
            return

        # Use a short timeout for the initial connection attempt
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        
        db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
        
        # Initialize Beanie without explicitly waiting for the server
        # This prevents the 10s Vercel timeout from killing the function if DB is slow
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
        logger.info(f"Beanie initialized for database '{db_name}'.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # We don't raise here to allow the app to at least start and show /health
