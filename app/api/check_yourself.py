from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/check-yourself", tags=["check-yourself"])

@router.get("")
def get_modules(current_user = Depends(get_current_user)):
    return ["assignment", "quiz"]
