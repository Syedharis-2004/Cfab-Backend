from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api.auth import get_admin_user
from app.models.assignment import Assignment, AssignmentType
from app.models.coding_assignment import CodingAssignment
from app.models.test_case import TestCase
from app.models.user import User
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/coding-assignment", tags=["admin-coding-assignment"])

@router.post("/upload")
async def upload_coding_assignment(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    """
    Admin uploads a JSON file for a coding assignment.
    Format:
    {
      "title": "...",
      "description": "...",
      "function_name": "solve",
      "test_cases": [
        {"input": "...", "expected_output": "...", "is_hidden": false}
      ]
    }
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")

    try:
        content = await file.read()
        data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")

    # Basic Validation
    required_fields = ["title", "description", "function_name", "test_cases"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    # 1. Create main Assignment entry
    assignment = Assignment(
        title=data["title"],
        assignment_type=AssignmentType.CODING
    )
    await assignment.insert()

    # 2. Create detailed CodingAssignment entry
    coding_assignment = CodingAssignment(
        assignment_id=assignment.id,
        title=data["title"],
        description=data["description"],
        function_name=data["function_name"],
        starter_code=data.get("starter_code"),
        language=data.get("language", "python")
    )
    await coding_assignment.insert()

    # 3. Create TestCases
    for tc_data in data["test_cases"]:
        test_case = TestCase(
            assignment_id=assignment.id,
            input=tc_data["input"],
            expected_output=tc_data["expected_output"],
            is_hidden=tc_data.get("is_hidden", False)
        )
        await test_case.insert()

    logger.info(f"Coding assignment '{data['title']}' created by admin {current_admin.email}")
    
    return {
        "message": "Coding assignment uploaded successfully",
        "assignment_id": str(assignment.id),
        "test_case_count": len(data["test_cases"])
    }
