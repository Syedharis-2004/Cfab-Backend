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
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Explicitly get database name from URL if possible
        db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
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
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
