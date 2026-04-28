from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
import logging
import ssl
import certifi

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

        # Build MongoDB URL — ensure it has the correct SSL/TLS params for Atlas
        mongo_url = settings.MONGODB_URL
        
        # If the URL doesn't already have tls params, ensure they're added
        # MongoDB Atlas requires TLS; Vercel's environment needs explicit SSL context
        if "tls=" not in mongo_url and "ssl=" not in mongo_url:
            connector = "&" if "?" in mongo_url else "?"
            mongo_url = f"{mongo_url}{connector}tls=true&tlsAllowInvalidCertificates=false"

        # Create SSL context using certifi's CA bundle
        # This fixes the TLSV1_ALERT_INTERNAL_ERROR on Vercel's Python runtime
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            tls=True,
            tlsCAFile=certifi.where(),
        )
        
        # Extract db name from URL or use default
        try:
            db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
            if not db_name or db_name.strip() == "":
                db_name = "check_yourself"
        except Exception:
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
        _db_initialized = False
        raise e
