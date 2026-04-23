from fastapi import APIRouter, Depends
from app.api.auth import get_current_user

router = APIRouter(prefix="/check-yourself", tags=["check-yourself"])

@router.get("")
async def get_modules(current_user = Depends(get_current_user)):
    return ["assignment", "quiz"]
