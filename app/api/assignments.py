"""
Assignments API — handles both PDF and Coding assignment types.

Existing PDF endpoints are fully preserved.
New endpoints support coding assignments and admin management.
"""

import os
import shutil
import logging
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from beanie import PydanticObjectId

from app.api.auth import get_current_user, get_admin_user
from app.core.config import settings
from app.models.assignment import Assignment, AssignmentType
from app.models.test_case import TestCase
from app.schemas.assignment import (
    AssignmentListItem,
    PDFAssignmentRead,
    CodingAssignmentRead,
    CodingAssignmentCreate,
    TestCaseRead,
    Assignment as AssignmentSchema,  # backward-compat alias
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assignments", tags=["assignments"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _enrich_coding(assignment: Assignment) -> CodingAssignmentRead:
    """Attach visible test cases to a coding assignment response."""
    test_cases = await TestCase.find(
        TestCase.assignment_id == assignment.id
    ).to_list()

    # Only expose non-hidden test cases to users
    visible = [tc for tc in test_cases if not tc.is_hidden]

    return CodingAssignmentRead(
        id=assignment.id,
        title=assignment.title,
        assignment_type=assignment.assignment_type,
        description=assignment.description,
        starter_code=assignment.starter_code,
        language=assignment.language,
        created_at=assignment.created_at,
        test_cases=[
            TestCaseRead(id=tc.id, input=tc.input, expected_output=tc.expected_output, is_hidden=tc.is_hidden)
            for tc in visible
        ],
    )


# ---------------------------------------------------------------------------
# GET /assignments  — list all (PDF + Coding)
# ---------------------------------------------------------------------------

@router.get("", response_model=List[AssignmentListItem])
async def get_assignments(current_user=Depends(get_current_user)):
    """Return a lightweight list of all assignments (both PDF and Coding)."""
    assignments = await Assignment.find_all().to_list()
    return [
        AssignmentListItem(
            id=a.id,
            title=a.title,
            assignment_type=a.assignment_type,
            created_at=a.created_at,
        )
        for a in assignments
    ]


# ---------------------------------------------------------------------------
# GET /assignments/search  — search by title
# ---------------------------------------------------------------------------

@router.get("/search", response_model=List[AssignmentListItem])
async def search_assignments(title: str, current_user=Depends(get_current_user)):
    """Search assignments by title (case-insensitive)."""
    assignments = await Assignment.find(
        {"title": {"$regex": title, "$options": "i"}}
    ).to_list()
    return [
        AssignmentListItem(
            id=a.id,
            title=a.title,
            assignment_type=a.assignment_type,
            created_at=a.created_at,
        )
        for a in assignments
    ]


# ---------------------------------------------------------------------------
# GET /assignments/{id}  — detail view (PDF returns file, Coding returns JSON)
# ---------------------------------------------------------------------------

@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: PydanticObjectId,
    current_user=Depends(get_current_user),
):
    """
    Return assignment detail.
    - PDF assignments: streams the PDF file.
    - Coding assignments: returns JSON with description and visible test cases.
    """
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.assignment_type == AssignmentType.PDF:
        if not assignment.pdf_path or not os.path.exists(assignment.pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found on server")
        return FileResponse(
            assignment.pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(assignment.pdf_path),
        )

    # Coding assignment
    return await _enrich_coding(assignment)


# ---------------------------------------------------------------------------
# POST /assignments/upload  — Admin: upload a PDF assignment
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=AssignmentSchema)
async def upload_assignment(title: str, file: UploadFile = File(...), current_admin=Depends(get_admin_user)):
    """Admin endpoint: upload a PDF assignment."""
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_assignment = Assignment(
        title=title,
        assignment_type=AssignmentType.PDF,
        pdf_path=file_path,
    )
    await db_assignment.insert()
    logger.info("PDF assignment created: %s", db_assignment.id)
    return AssignmentListItem(
        id=db_assignment.id,
        title=db_assignment.title,
        assignment_type=db_assignment.assignment_type,
        created_at=db_assignment.created_at,
    )


# ---------------------------------------------------------------------------
# POST /assignments/coding  — Admin: create a coding assignment
# ---------------------------------------------------------------------------

@router.post("/coding", response_model=CodingAssignmentRead)
async def create_coding_assignment(payload: CodingAssignmentCreate, current_admin=Depends(get_admin_user)):
    """Admin endpoint: create a coding assignment with test cases."""
    db_assignment = Assignment(
        title=payload.title,
        assignment_type=AssignmentType.CODING,
        description=payload.description,
        starter_code=payload.starter_code,
        language=payload.language or "python",
    )
    await db_assignment.insert()

    # Persist test cases
    created_tcs = []
    for tc in payload.test_cases:
        db_tc = TestCase(
            assignment_id=db_assignment.id,
            input=tc.input,
            expected_output=tc.expected_output,
            is_hidden=tc.is_hidden,
        )
        await db_tc.insert()
        created_tcs.append(db_tc)

    logger.info(
        "Coding assignment created: %s with %d test cases",
        db_assignment.id,
        len(created_tcs),
    )

    visible = [tc for tc in created_tcs if not tc.is_hidden]
    return CodingAssignmentRead(
        id=db_assignment.id,
        title=db_assignment.title,
        assignment_type=db_assignment.assignment_type,
        description=db_assignment.description,
        starter_code=db_assignment.starter_code,
        language=db_assignment.language,
        created_at=db_assignment.created_at,
        test_cases=[
            TestCaseRead(id=tc.id, input=tc.input, expected_output=tc.expected_output, is_hidden=tc.is_hidden)
            for tc in visible
        ],
    )
