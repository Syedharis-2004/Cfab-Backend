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
async def log_requests_and_init_db(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    # Skip DB init for health check and root
    if request.url.path not in ["/health", "/", "/docs", "/openapi.json", "/api/health"]:
        try:
            await init_db()
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"detail": f"Database connection error: {str(e)}"}
            )
    
    response = await call_next(request)
    return response

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
def health_check():
    return {"status": "ok"}
