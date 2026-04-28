from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.schemas.quiz import QuizResponse, QuizAttempt, QuizResult, QuestionResponse, QuestionResult
from app.models.user import User

router = APIRouter(prefix="/quiz", tags=["quiz"])

async def _get_quiz_response(quiz: Quiz) -> QuizResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[QuestionResponse(
            id=q.id,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d
        ) for q in questions]
    )

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(current_user: User = Depends(get_current_user)):
    """
    Fetch a list of all available interactive quizzes.
    Includes questions and multiple-choice options (but NOT correct answers).
    """
    quizzes = await Quiz.find_all().to_list()
    return [await _get_quiz_response(q) for q in quizzes]

@router.get("/{id}", response_model=QuizResponse)
async def get_quiz(id: str, current_user: User = Depends(get_current_user)):
    """
    Retrieve details for a specific quiz by its ID.
    Returns questions and options — correct answers are hidden from users.
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return await _get_quiz_response(quiz)

@router.post("/{id}/submit", response_model=QuizResult)
async def submit_quiz(id: str, attempt: QuizAttempt, current_user: User = Depends(get_current_user)):
    """
    Submit answers for a quiz attempt.

    - Compares each user answer against the stored correct answer
    - Returns full per-question breakdown: your answer, correct answer, and is_correct
    - Returns total score, percentage, and pass/fail status (pass = 50%+)
    
    **Request body example:**
    ```json
    {
      "answers": [
        {"question_id": "<id>", "selected_answer": "A"},
        {"question_id": "<id>", "selected_answer": "C"}
      ]
    }
    ```
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    if not questions:
        raise HTTPException(status_code=400, detail="This quiz has no questions.")

    # Build a fast lookup: question_id -> QuizQuestion object
    question_map = {str(q.id): q for q in questions}

    score = 0
    total = len(questions)
    breakdown = []

    for answer in attempt.answers:
        q = question_map.get(str(answer.question_id))
        if not q:
            # Skip unknown question IDs gracefully
            continue

        user_choice = answer.selected_answer.strip().upper()
        correct_choice = q.correct_answer.strip().upper()
        is_correct = (user_choice == correct_choice)

        if is_correct:
            score += 1

        # Save per-question answer to DB for history/review
        ua = UserAnswer(
            user_id=current_user.id,
            quiz_id=quiz.id,
            question_id=q.id,
            selected_answer=user_choice,
            correct_answer=correct_choice,
            is_correct=is_correct,
        )
        await ua.insert()

        breakdown.append(QuestionResult(
            question_id=str(q.id),
            question_text=q.question,
            your_answer=user_choice,
            correct_answer=correct_choice,
            is_correct=is_correct,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
        ))

    percentage = round((score / total * 100), 2) if total > 0 else 0.0

    return QuizResult(
        score=score,
        total=total,
        percentage=percentage,
        passed=percentage >= 50,
        breakdown=breakdown,
    )
