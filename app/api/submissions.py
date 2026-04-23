"""
Coding Submissions API.

POST /coding-assignments/submit  — submit code for evaluation
GET  /coding-assignments/submissions/{id}  — poll result
GET  /coding-assignments/my-submissions    — list current user's submissions
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId

from app.api.auth import get_current_user
from app.models.assignment import Assignment, AssignmentType
from app.models.submission import Submission, SubmissionStatus
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coding-assignments", tags=["coding-assignments"])


# ---------------------------------------------------------------------------
# POST /coding-assignments/submit
# ---------------------------------------------------------------------------

@router.post("/submit", response_model=SubmissionStatusResponse, status_code=202)
async def submit_code(
    payload: SubmissionCreate,
    current_user=Depends(get_current_user),
):
    """
    Submit code for a coding assignment.

    Returns immediately with status=pending and a submission ID.
    Poll GET /coding-assignments/submissions/{id} to get the result.
    """
    # Validate assignment exists and is a coding type
    assignment = await Assignment.get(payload.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.assignment_type != AssignmentType.CODING:
        raise HTTPException(
            status_code=400,
            detail="This assignment is not a coding assignment. Use the PDF endpoint.",
        )

    # Persist the submission
    submission = Submission(
        user_id=current_user.id,
        assignment_id=payload.assignment_id,
        code=payload.code,
        language=payload.language,
        status=SubmissionStatus.PENDING,
    )
    await submission.insert()

    # Dispatch the Celery evaluation task (non-blocking)
    try:
        from app.worker.tasks import evaluate_submission
        task = evaluate_submission.delay(str(submission.id))
        submission.celery_task_id = task.id
        await submission.save()
        logger.info(
            "Submission %s dispatched to Celery task %s", submission.id, task.id
        )
    except Exception as exc:
        # If Celery/Redis is unavailable, mark as error but don't crash the API
        logger.error("Failed to dispatch Celery task: %s", exc)
        submission.status = SubmissionStatus.ERROR
        submission.error_message = "Evaluation service unavailable. Please try again later."
        await submission.save()

    return SubmissionStatusResponse(
        id=submission.id,
        status=submission.status,
        score=submission.score,
        total_cases=submission.total_cases,
        passed_cases=submission.passed_cases,
        error_message=submission.error_message,
        evaluated_at=submission.evaluated_at,
    )


# ---------------------------------------------------------------------------
# GET /coding-assignments/submissions/{id}  — poll result
# ---------------------------------------------------------------------------

@router.get("/submissions/{submission_id}", response_model=SubmissionStatusResponse)
async def get_submission_status(
    submission_id: PydanticObjectId,
    current_user=Depends(get_current_user),
):
    """Poll the status and result of a specific submission."""
    submission = await Submission.get(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Users can only see their own submissions
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return SubmissionStatusResponse(
        id=submission.id,
        status=submission.status,
        score=submission.score,
        total_cases=submission.total_cases,
        passed_cases=submission.passed_cases,
        error_message=submission.error_message,
        evaluated_at=submission.evaluated_at,
    )


# ---------------------------------------------------------------------------
# GET /coding-assignments/submissions/{id}/code  — full submission with code
# ---------------------------------------------------------------------------

@router.get("/submissions/{submission_id}/code", response_model=SubmissionRead)
async def get_submission_detail(
    submission_id: PydanticObjectId,
    current_user=Depends(get_current_user),
):
    """Return the full submission including the submitted code."""
    submission = await Submission.get(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return submission


# ---------------------------------------------------------------------------
# GET /coding-assignments/my-submissions  — list user's own submissions
# ---------------------------------------------------------------------------

@router.get("/my-submissions", response_model=List[SubmissionStatusResponse])
async def list_my_submissions(
    current_user=Depends(get_current_user),
    limit: int = 20,
):
    """Return the current user's most recent submissions (up to limit)."""
    submissions = (
        await Submission.find(Submission.user_id == current_user.id)
        .sort("-submitted_at")
        .limit(limit)
        .to_list()
    )
    return [
        SubmissionStatusResponse(
            id=s.id,
            status=s.status,
            score=s.score,
            total_cases=s.total_cases,
            passed_cases=s.passed_cases,
            error_message=s.error_message,
            evaluated_at=s.evaluated_at,
        )
        for s in submissions
    ]
