from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, check_yourself, assignments, quiz

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Check Yourself API")

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

@app.get("/")
def read_root():
    return {"message": "Welcome to Check Yourself API"}
