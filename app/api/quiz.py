from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.utils.logger import logger
from app.schemas.quiz import (
    QuizResponse, QuestionResponse, QuizSubmitRequest
)
from app.models.user import User
from app.utils.mongo_serializer import serialize_doc, serialize_list

router = APIRouter(prefix="/quiz", tags=["quiz"])

async def _get_quiz_response(quiz: Quiz) -> QuizResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "questions": [
            {
                "id": str(q.id),
                "question": q.question,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
            }
            for q in questions
        ],
    }

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(current_user: User = Depends(get_current_user)):
    """
    Get all available quizzes.
    Correct answers are NOT included.
    """
    from app.core.database import _db_initialized
    if not _db_initialized:
        logger.error("Database not initialized. Cannot fetch quizzes.")
        raise HTTPException(
            status_code=503, 
            detail="Database connection is currently unavailable. Please try again later."
        )

    try:
        quizzes = await Quiz.find_all().to_list()
        results = [await _get_quiz_response(q) for q in quizzes]
        return serialize_list(results)
    except Exception as e:
        logger.error(f"Quiz List Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quizzes due to a server error")


@router.get("/{id}", response_model=QuizResponse)
async def get_quiz(id: str, current_user: User = Depends(get_current_user)):
    """
    Get a single quiz by ID.
    """
    try:
        quiz = await Quiz.get(id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        response_data = await _get_quiz_response(quiz)
        return serialize_doc(response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz Get Error (ID: {id}): {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quiz details")

@router.post("/{id}/submit")
async def submit_quiz(
    id: PydanticObjectId,
    submission: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit answers for a quiz.
    Input matches the frontend format: URL contains quiz ID, body contains answers list.
    """
    try:
        quiz = await Quiz.get(id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
        if not questions:
            raise HTTPException(status_code=400, detail="This quiz has no questions.")

        question_map = {str(q.id): q for q in questions}

        score = 0
        total = len(questions)

        for answer in submission.answers:
            q = question_map.get(str(answer.question_id))
            if not q:
                continue

            if answer.selected_answer.upper() == q.correct_answer.upper():
                score += 1

        return {
            "score": score,
            "total": total,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz Submit Error (ID: {id}): {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")
