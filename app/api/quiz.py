from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.schemas.quiz import (
    QuizResponse, QuestionResponse, QuizSubmitRequest
)
from app.models.user import User

router = APIRouter(prefix="/quiz", tags=["quiz"])

async def _get_quiz_response(quiz: Quiz) -> QuizResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[
            QuestionResponse(
                id=q.id,
                question=q.question,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
            )
            for q in questions
        ],
    )

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(current_user: User = Depends(get_current_user)):
    """
    Get all available quizzes.
    Correct answers are NOT included.
    """
    quizzes = await Quiz.find_all().to_list()
    return [await _get_quiz_response(q) for q in quizzes]

@router.get("/{id}", response_model=QuizResponse)
async def get_quiz(id: str, current_user: User = Depends(get_current_user)):
    """
    Get a single quiz by ID.
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return await _get_quiz_response(quiz)

@router.post("/submit")
async def submit_quiz(
    submission: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit answers for a quiz.
    Input matches the requested format: {quiz_id, answers: [{question_id, selected}]}
    """
    quiz = await Quiz.get(submission.quiz_id)
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

        if answer.selected.upper() == q.correct_answer.upper():
            score += 1

    return {
        "score": score,
        "total": total
    }


