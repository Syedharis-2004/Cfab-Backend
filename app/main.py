import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import init_db
from app.api import auth, check_yourself, assignments, quiz, admin_quiz, admin_assignments
from app.api import submissions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Application startup complete.")
    yield

app = FastAPI(
    title="Check Yourself API",
    description="Backend for the Check Yourself module — PDF assignments, quizzes, and coding practice.",
    version="2.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(check_yourself.router)
app.include_router(assignments.router)
app.include_router(quiz.router)
app.include_router(admin_quiz.router)
app.include_router(admin_assignments.router)
app.include_router(submissions.router)

# # Mount static files for frontend
# app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Check Yourself API v2",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
