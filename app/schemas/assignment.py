from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId
from app.models.assignment import AssignmentType


# ---------------------------------------------------------------------------
# Test Case Schemas
# ---------------------------------------------------------------------------

class TestCaseCreate(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False


class TestCaseRead(TestCaseCreate):
    id: PydanticObjectId

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Assignment Schemas
# ---------------------------------------------------------------------------

class AssignmentBase(BaseModel):
    title: str
    assignment_type: AssignmentType = AssignmentType.PDF


# --- PDF Assignment ---
class PDFAssignmentCreate(AssignmentBase):
    assignment_type: AssignmentType = AssignmentType.PDF
    file_path: str


# --- Coding Assignment ---
class CodingAssignmentCreate(AssignmentBase):
    assignment_type: AssignmentType = AssignmentType.CODING
    description: str
    function_name: str
    starter_code: Optional[str] = None
    language: Optional[str] = "python"
    test_cases: List[TestCaseCreate] = []


# --- Read Schemas ---
class AssignmentListItem(BaseModel):
    """Lightweight schema for listing all assignments."""
    id: PydanticObjectId
    title: str
    assignment_type: AssignmentType
    created_at: datetime

    class Config:
        from_attributes = True


class PDFAssignmentRead(AssignmentBase):
    """Full schema for a PDF assignment."""
    id: PydanticObjectId
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CodingAssignmentRead(AssignmentBase):
    """Full schema for a coding assignment (includes test cases)."""
    id: PydanticObjectId
    description: Optional[str]
    function_name: Optional[str]
    starter_code: Optional[str]
    language: Optional[str]
    created_at: datetime
    test_cases: List[TestCaseRead] = []

    class Config:
        from_attributes = True


# Backward-compatible schema alias used by legacy endpoints
class Assignment(AssignmentListItem):
    pass
