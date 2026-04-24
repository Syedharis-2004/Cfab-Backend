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
from app.models.coding_assignment import CodingAssignment
from app.models.test_case import TestCase
from app.schemas.assignment import (
    AssignmentListItem,
    PDFAssignmentRead,
    CodingAssignmentRead,
    CodingAssignmentCreate,
    TestCaseRead,
    Assignment as AssignmentSchema,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assignments", tags=["assignments"])

async def _enrich_coding(assignment: Assignment) -> CodingAssignmentRead:
    """Attach detailed metadata and visible test cases to a coding assignment."""
    coding_meta = await CodingAssignment.find_one(
        CodingAssignment.assignment_id == assignment.id
    )
    if not coding_meta:
        # Fallback if meta is missing for some reason
        return CodingAssignmentRead(
            id=assignment.id,
            title=assignment.title,
            assignment_type=assignment.assignment_type,
            created_at=assignment.created_at,
            test_cases=[]
        )

    test_cases = await TestCase.find(
        TestCase.assignment_id == assignment.id
    ).to_list()

    # Only expose non-hidden test cases to users
    visible = [tc for tc in test_cases if not tc.is_hidden]

    return CodingAssignmentRead(
        id=assignment.id,
        title=assignment.title,
        assignment_type=assignment.assignment_type,
        description=coding_meta.description,
        function_name=coding_meta.function_name,
        starter_code=coding_meta.starter_code,
        language=coding_meta.language,
        created_at=assignment.created_at,
        test_cases=[
            TestCaseRead(id=tc.id, input=tc.input, expected_output=tc.expected_output, is_hidden=tc.is_hidden)
            for tc in visible
        ],
    )

@router.get("", response_model=List[AssignmentListItem])
async def get_assignments(current_user=Depends(get_current_user)):
    """Return a lightweight list of all assignments."""
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

@router.get("/search", response_model=List[AssignmentListItem])
async def search_assignments(title: str, current_user=Depends(get_current_user)):
    """Search assignments by title."""
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

@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: PydanticObjectId,
    current_user=Depends(get_current_user),
):
    """Return assignment detail."""
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.assignment_type == AssignmentType.PDF:
        if not assignment.file_path or not os.path.exists(assignment.file_path):
            raise HTTPException(status_code=404, detail="PDF file not found on server")
        return FileResponse(
            assignment.file_path,
            media_type="application/pdf",
            filename=os.path.basename(assignment.file_path),
        )

    # Coding assignment
    return await _enrich_coding(assignment)

@router.post("/upload", response_model=AssignmentListItem)
async def upload_assignment(title: str, file: UploadFile = File(...), current_admin=Depends(get_admin_user)):
    """Admin: upload a PDF assignment."""
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_assignment = Assignment(
        title=title,
        assignment_type=AssignmentType.PDF,
        file_path=file_path,
    )
    await db_assignment.insert()
    return db_assignment

@router.post("/coding", response_model=CodingAssignmentRead)
async def create_coding_assignment(payload: CodingAssignmentCreate, current_admin=Depends(get_admin_user)):
    """Admin: create a coding assignment via JSON payload."""
    db_assignment = Assignment(
        title=payload.title,
        assignment_type=AssignmentType.CODING,
    )
    await db_assignment.insert()

    coding_meta = CodingAssignment(
        assignment_id=db_assignment.id,
        title=payload.title,
        description=payload.description,
        function_name=payload.function_name,
        starter_code=payload.starter_code,
        language=payload.language or "python",
    )
    await coding_meta.insert()

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

    return await _enrich_coding(db_assignment)
