from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
import logging

logger = logging.getLogger(__name__)

# List of all Beanie document models for initialization
from app.models.user import User
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.models.test_case import TestCase
from app.models.submission import Submission


async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=client.get_default_database(),
            document_models=[
                User,
                Assignment,
                Quiz,
                UserAnswer,
                TestCase,
                Submission,
            ]
        )
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
