"""
Celery tasks for evaluating coding submissions.

Each task:
  1. Loads the submission + test cases from MongoDB.
  2. Runs the code via the sandbox service.
  3. Writes the result back to MongoDB.

Because Celery workers are synchronous, we use motor's `asyncio.run` adapter
rather than calling async Beanie methods directly.
"""

import asyncio
import logging
from datetime import datetime, timezone

from celery.exceptions import SoftTimeLimitExceeded
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId

from app.worker.celery_app import celery_app
from app.core.config import settings
from app.services.sandbox import evaluate_code

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Async helpers (Celery tasks are sync; we run a fresh event-loop per task)
# ---------------------------------------------------------------------------

async def _init_beanie_for_worker():
    """Initialize Beanie with all document models inside the worker process."""
    from app.models.user import User
    from app.models.assignment import Assignment
    from app.models.quiz import Quiz
    from app.models.user_answer import UserAnswer
    from app.models.test_case import TestCase
    from app.models.submission import Submission

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[User, Assignment, Quiz, UserAnswer, TestCase, Submission],
    )


async def _evaluate(submission_id: str):
    """Core async evaluation logic."""
    from app.models.submission import Submission, SubmissionStatus
    from app.models.test_case import TestCase

    await _init_beanie_for_worker()

    sub = await Submission.get(PydanticObjectId(submission_id))
    if not sub:
        logger.error("Submission %s not found.", submission_id)
        return

    # Mark as running
    sub.status = SubmissionStatus.RUNNING
    await sub.save()

    # Fetch ALL test cases for this assignment (including hidden)
    test_cases = await TestCase.find(
        TestCase.assignment_id == sub.assignment_id
    ).to_list()

    if not test_cases:
        logger.warning("No test cases found for assignment %s.", sub.assignment_id)
        sub.status = SubmissionStatus.ERROR
        sub.error_message = "No test cases configured for this assignment."
        sub.evaluated_at = datetime.now(timezone.utc)
        await sub.save()
        return

    # Build the list of dicts the sandbox service expects
    tc_dicts = [
        {"input": tc.input, "expected_output": tc.expected_output}
        for tc in test_cases
    ]

    try:
        result = evaluate_code(sub.code, tc_dicts)
    except SoftTimeLimitExceeded:
        sub.status = SubmissionStatus.TIME_LIMIT_EXCEEDED
        sub.error_message = "Execution exceeded the time limit."
        sub.evaluated_at = datetime.now(timezone.utc)
        await sub.save()
        return
    except Exception as exc:
        logger.exception("Unexpected error during evaluation: %s", exc)
        sub.status = SubmissionStatus.ERROR
        sub.error_message = str(exc)
        sub.evaluated_at = datetime.now(timezone.utc)
        await sub.save()
        return

    # Persist results
    sub.passed_cases = result["passed"]
    sub.total_cases = result["total"]
    sub.score = result["score"]
    sub.error_message = result.get("error_message")
    sub.evaluated_at = datetime.now(timezone.utc)

    if result["passed"] == result["total"]:
        sub.status = SubmissionStatus.ACCEPTED
    elif result.get("error_message"):
        sub.status = SubmissionStatus.RUNTIME_ERROR
    else:
        sub.status = SubmissionStatus.WRONG_ANSWER

    await sub.save()
    logger.info(
        "Submission %s evaluated: %s (%d/%d) score=%d",
        submission_id,
        sub.status,
        sub.passed_cases,
        sub.total_cases,
        sub.score,
    )


# ---------------------------------------------------------------------------
# Celery task definition
# ---------------------------------------------------------------------------

@celery_app.task(bind=True, name="evaluate_submission", max_retries=2, default_retry_delay=5)
def evaluate_submission(self, submission_id: str):
    """
    Celery task: evaluate a coding submission.

    Args:
        submission_id: String representation of the MongoDB ObjectId.
    """
    logger.info("Starting evaluation for submission %s", submission_id)
    try:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_evaluate(submission_id))
        except RuntimeError:
            asyncio.run(_evaluate(submission_id))
    except SoftTimeLimitExceeded:
        logger.warning("Soft time limit exceeded for submission %s", submission_id)
        raise
    except Exception as exc:
        logger.exception("Task failed for submission %s: %s", submission_id, exc)
        raise self.retry(exc=exc)
