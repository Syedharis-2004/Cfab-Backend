from beanie import Document
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
from pydantic import Field


class AssignmentType(str, Enum):
    PDF = "pdf"
    CODING = "coding"




class Assignment(Document):
    title: str
    description: Optional[str] = None
    assignment_type: AssignmentType = AssignmentType.PDF
    file_path: Optional[str] = None # For PDF practice
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "assignments"
