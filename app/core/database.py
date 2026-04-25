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

        logger.info(f"Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Explicitly get database name from URL if possible
        db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
        
        # Test connection
        await client.server_info()
        
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
        logger.info(f"Database '{db_name}' initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # In a serverless environment, we might want to log but not necessarily crash the whole process 
        # if the DB is temporarily down, though for this app it's critical.
        raise
