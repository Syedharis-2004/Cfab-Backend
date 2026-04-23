from beanie import Document, PydanticObjectId
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import Field


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    ERROR = "error"


class Submission(Document):
    user_id: PydanticObjectId
    assignment_id: PydanticObjectId
    code: str
    language: str = "python"
    status: SubmissionStatus = SubmissionStatus.PENDING
    score: int = 0               # percentage: 0-100
    total_cases: int = 0
    passed_cases: int = 0
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evaluated_at: Optional[datetime] = None

    class Settings:
        name = "submissions"
