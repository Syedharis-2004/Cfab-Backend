import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import init_db
from app.api import auth, check_yourself, assignments, quiz, admin_quiz, admin_assignments, study, time_management
from app.api import submissions
from app.routes import solved_assignment, test_gemini

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Application startup: Database initialized via lifespan.")
        
        # Log all registered routes
        logger.info("Registered Routes:")
        for route in app.routes:
            methods = getattr(route, "methods", None)
            path = getattr(route, "path", None)
            logger.info(f"  {methods} {path}")
            
    except Exception as e:
        logger.warning(f"Application startup: Database initialization failed: {e}")
    
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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
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
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": error_msg,
            "type": type(exc).__name__
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"🚀 {request.method} {request.url.path}")
    
    # We no longer force init_db on every request to avoid 503 crashes.
    # init_db is handled in lifespan with retries.
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Middleware Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Critical Middleware Error", "message": str(e)}
        )

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(check_yourself.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(admin_quiz.router, prefix="/api")
app.include_router(admin_assignments.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(study.router, prefix="/api")
app.include_router(time_management.router, prefix="/api")
app.include_router(solved_assignment.router)
app.include_router(test_gemini.router)

# # Mount static files for frontend
# app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Check Yourself API v2",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    from app.core.database import _db_initialized
    from app.core.redis_service import redis_service
    
    db_status = "connected" if _db_initialized else "disconnected"
    redis_available = await redis_service.is_available()
    redis_status = "connected" if redis_available else "disconnected"
    
    status_code = 200
    if not _db_initialized:
        status_code = 503
        
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if _db_initialized else "degraded",
            "database": db_status,
            "redis": redis_status,
            "version": "2.0.1"
        }
    )
