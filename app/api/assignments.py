import os
import shutil
import logging
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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
    """
    Retrieve a list of all assignments (both PDF and Coding types).
    Returns basic metadata only.
    """
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
    """
    Search for assignments by title using a case-insensitive keyword search.
    """
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
    """
    Retrieve the full details of an assignment.
    For PDF assignments, it returns metadata and the file path.
    For Coding assignments, it returns the problem description and visible test cases.
    """
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.assignment_type == AssignmentType.PDF:
        return PDFAssignmentRead(
            id=assignment.id,
            title=assignment.title,
            description=assignment.description,
            assignment_type=assignment.assignment_type,
            file_path=assignment.file_path,
            created_at=assignment.created_at
        )

    # Coding assignment
    return await _enrich_coding(assignment)

@router.get("/{assignment_id}/file")
async def get_assignment_file(
    assignment_id: PydanticObjectId,
    current_user=Depends(get_current_user),
):
    """Return the raw PDF file."""
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.assignment_type != AssignmentType.PDF:
        raise HTTPException(status_code=400, detail="Not a PDF assignment")

    if not assignment.file_path or not os.path.exists(assignment.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on server")
        
    return FileResponse(
        assignment.file_path,
        media_type="application/pdf",
        filename=os.path.basename(assignment.file_path),
    )

@router.post("/upload", response_model=PDFAssignmentRead)
async def upload_assignment(
    title: str = Form(...), 
    description: Union[str, None] = Form(None),
    file: UploadFile = File(...), 
    current_admin=Depends(get_admin_user)
):
    """
    Admin: Upload a new practice assignment in PDF format.
    The file is stored on the server and its metadata is saved to the database.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_assignment = Assignment(
        title=title,
        description=description,
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


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: PydanticObjectId,
    current_admin=Depends(get_admin_user),
):
    """Admin: Delete an assignment and its associated file/metadata."""
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.assignment_type == AssignmentType.PDF:
        # Delete file from disk
        if assignment.file_path and os.path.exists(assignment.file_path):
            try:
                os.remove(assignment.file_path)
            except Exception as e:
                logger.error(f"Error deleting file {assignment.file_path}: {e}")
    
    elif assignment.assignment_type == AssignmentType.CODING:
        # Delete coding metadata and test cases
        await CodingAssignment.find(CodingAssignment.assignment_id == assignment.id).delete()
        await TestCase.find(TestCase.assignment_id == assignment.id).delete()
        # Also could delete submissions, but usually better to keep them or handle cascade
        # For now, let's just delete the main assignment record and its metadata

    await assignment.delete()
    return {"message": "Assignment deleted successfully"}
