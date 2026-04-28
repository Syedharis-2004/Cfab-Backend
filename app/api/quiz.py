from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.schemas.quiz import (
    QuizResponse, QuizAttempt, QuizResult,
    QuestionResponse, QuestionResult
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
                options=q.options,
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

@router.post("/{id}/submit", response_model=QuizResult)
async def submit_quiz(
    id: str,
    attempt: QuizAttempt,
    current_user: User = Depends(get_current_user),
):
    """
    Submit answers for a quiz.
    `selected_option` should be the exact text of the chosen option.
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    if not questions:
        raise HTTPException(status_code=400, detail="This quiz has no questions.")

    question_map = {str(q.id): q for q in questions}

    score = 0
    total = len(questions)
    breakdown: List[QuestionResult] = []

    for answer in attempt.answers:
        q = question_map.get(str(answer.question_id))
        if not q:
            continue

        selected = answer.selected_option.strip()
        correct = q.correct_answer.strip()
        is_correct = selected == correct

        if is_correct:
            score += 1

        # Save record
        ua = UserAnswer(
            user_id=current_user.id,
            quiz_id=quiz.id,
            question_id=q.id,
            selected_answer=selected,
            correct_answer=correct,
            is_correct=is_correct,
        )
        await ua.insert()

        breakdown.append(
            QuestionResult(
                question_id=str(q.id),
                question_text=q.question,
                options=q.options,
                selected_option=selected,
                correct_option=correct,
                is_correct=is_correct,
            )
        )

    percentage = round((score / total * 100), 2) if total > 0 else 0.0

    return QuizResult(
        score=score,
        total=total,
        percentage=percentage,
        passed=percentage >= 50,
        breakdown=breakdown,
    )
