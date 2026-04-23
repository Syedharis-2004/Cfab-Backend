from beanie import Document
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
from pydantic import Field


class AssignmentType(str, Enum):
    PDF = "pdf"
    CODING = "coding"


class TestCase(Document):
    """Embedded test case for coding assignments."""
    input: str
    expected_output: str
    is_hidden: bool = False

    class Settings:
        name = "test_cases"


class Assignment(Document):
    title: str
    assignment_type: AssignmentType = AssignmentType.PDF
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # PDF assignment fields
    pdf_path: Optional[str] = None

    # Coding assignment fields
    description: Optional[str] = None  # Problem statement (markdown supported)
    starter_code: Optional[str] = None  # Optional boilerplate code
    language: Optional[str] = "python"  # Supported language

    class Settings:
        name = "assignments"
