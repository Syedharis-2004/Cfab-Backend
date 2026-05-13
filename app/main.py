import logging
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.utils.logger import logger
from app.api import auth, check_yourself, assignments, quiz, admin_quiz, admin_assignments, study, time_management
from app.api import submissions
from app.routes import solved_assignment, test_gemini

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

# Common CORS headers for fallback error responses
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "http://localhost:3000", # Default fallback
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
}


# Global Exception Handler for all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    
    # Log the full error for debugging
    logger.error(f"UNHANDLED EXCEPTION: {error_msg}\n{stack_trace}")
    
    # Determine status code
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_msg = exc.detail
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "detail": "An internal server error occurred." if status_code == 500 else error_msg,
            "message": error_msg,
            "type": type(exc).__name__
        },
        headers=CORS_HEADERS
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Safe request logging
    path = request.url.path
    method = request.method
    origin = request.headers.get("origin")
    logger.info(f"Incoming Request: {method} {path} from {origin}")
    
    # Dynamically set CORS origin for the log_requests error responses
    current_cors_headers = CORS_HEADERS.copy()
    if origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]:
        current_cors_headers["Access-Control-Allow-Origin"] = origin

    try:
        response = await call_next(request)
        logger.info(f"Response Status: {response.status_code} for {method} {path}")
        return response
    except Exception as e:
        # Prevent middleware crashes from taking down the app
        error_msg = str(e)
        logger.error(f"Middleware Error during {method} {path}: {error_msg}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "detail": "Critical Middleware Error",
                "message": error_msg
            },
            headers=current_cors_headers
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
