import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    logger.error(f"Unhandled Exception: {error_msg}\n{stack_trace}")
    
    # In production, you might want to hide the stack trace, 
    # but for debugging the 500 error on Vercel, we need more info.
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": error_msg,
            "type": type(exc).__name__
        }
    )

@app.middleware("http")
async def ensure_db_initialized(request: Request, call_next):
    # Skip DB init for health check and root
    if request.url.path not in ["/health", "/", "/docs", "/openapi.json"]:
        try:
            await init_db()
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"detail": f"Database connection error: {str(e)}"}
            )
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

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
