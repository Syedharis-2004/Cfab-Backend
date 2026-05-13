from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
from app.utils.logger import logger
import ssl
import certifi

# List of all Beanie document models for initialization
from app.models.user import User
from app.models.assignment import Assignment
from app.models.coding_assignment import CodingAssignment
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.models.test_case import TestCase
from app.models.submission import Submission
from app.models.study import Course, Lecture, StudyPlan, Progress
from app.models.solved_assignment import SolvedAssignment

import asyncio

_db_initialized = False

async def init_db():
    global _db_initialized
    if _db_initialized:
        return

    # Use a shorter timeout for local development if it's failing
    # but give it enough time for a real connection
    max_retries = 5
    retry_delay = 3 # seconds

    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")

    for attempt in range(max_retries):
        try:
            if not settings.MONGODB_URL:
                logger.error("❌ MONGODB_URL is missing in environment variables.")
                return

            mongo_url = settings.MONGODB_URL
            
            # Create SSL context if needed (for Atlas)
            kwargs = {
                "serverSelectionTimeoutMS": 5000, # 5 seconds is enough to fail fast if not running
                "connectTimeoutMS": 10000,
            }

            if "mongodb+srv" in mongo_url or "ssl=true" in mongo_url.lower() or "tls=true" in mongo_url.lower():
                kwargs["tls"] = True
                kwargs["tlsCAFile"] = certifi.where()

            client = AsyncIOMotorClient(mongo_url, **kwargs)
            
            # Extract db name
            try:
                db_name = mongo_url.split("/")[-1].split("?")[0] or "check_yourself"
            except Exception:
                db_name = "check_yourself"
            
            # Test connection before initializing Beanie
            await client.admin.command('ping')
            
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
                    Course,
                    Lecture,
                    StudyPlan,
                    Progress,
                    SolvedAssignment,
                ]
            )
            _db_initialized = True
            logger.info(f"✅ Beanie initialized successfully for database '{db_name}'.")
            return
        except Exception as e:
            logger.warning(f"⚠️ Database connection attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ CRITICAL: Database initialization failed after all retries.")
                logger.error("The application will continue to run but database-dependent features will be unavailable.")
                _db_initialized = False
                # We don't re-raise here to allow the app to start as requested in Task 7

