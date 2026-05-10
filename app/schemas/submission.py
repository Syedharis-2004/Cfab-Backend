from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from app.models.submission import SubmissionStatus


class SubmissionCreate(BaseModel):
    assignment_id: PydanticObjectId
    code: str
    language: str = "python"


class SubmissionRead(BaseModel):
    id: str
    user_id: str
    assignment_id: str
    code: str
    language: str
    status: SubmissionStatus
    score: int
    total_cases: int
    passed_cases: int
    error_message: Optional[str] = None
    submitted_at: datetime
    evaluated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionStatusResponse(BaseModel):
    """Lightweight response for polling submission status."""
    id: str
    status: SubmissionStatus
    score: int
    total_cases: int
    passed_cases: int
    error_message: Optional[str] = None
    evaluated_at: Optional[datetime] = None
