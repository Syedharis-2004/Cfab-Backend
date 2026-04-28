from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.schemas.quiz import (
    QuizResponse, QuizAttempt, QuizResult,
    QuestionResponse, QuestionResult, OptionItem
)
from app.models.user import User

router = APIRouter(prefix="/quiz", tags=["quiz"])


# ── Helper: build the 4-option list from a QuizQuestion document ──────────────

def _build_options(q: QuizQuestion) -> List[OptionItem]:
    return [
        OptionItem(key="A", text=q.option_a),
        OptionItem(key="B", text=q.option_b),
        OptionItem(key="C", text=q.option_c),
        OptionItem(key="D", text=q.option_d),
    ]


def _option_text(q: QuizQuestion, key: str) -> str:
    """Return the option text for a given key (A/B/C/D)."""
    mapping = {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d}
    return mapping.get(key.upper(), "")


# ── Shared builder ────────────────────────────────────────────────────────────

async def _get_quiz_response(quiz: Quiz) -> QuizResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[
            QuestionResponse(
                id=q.id,
                question=q.question,
                options=_build_options(q),
            )
            for q in questions
        ],
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(current_user: User = Depends(get_current_user)):
    """
    Get all available quizzes.
    Each question includes a labelled options list [A, B, C, D].
    Correct answers are NOT included.
    """
    quizzes = await Quiz.find_all().to_list()
    return [await _get_quiz_response(q) for q in quizzes]


@router.get("/{id}", response_model=QuizResponse)
async def get_quiz(id: str, current_user: User = Depends(get_current_user)):
    """
    Get a single quiz by ID.
    Returns questions with labelled options — correct answers hidden.
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

    Send one `selected_option` ("A"/"B"/"C"/"D") per question.

    **Request body:**
    ```json
    {
      "answers": [
        {"question_id": "<id>", "selected_option": "A"},
        {"question_id": "<id>", "selected_option": "C"}
      ]
    }
    ```

    **Response includes:**
    - `score`, `total`, `percentage`, `passed`
    - Per-question `breakdown` with:
      - `options` list
      - `selected_option` / `selected_option_text`
      - `correct_option` / `correct_option_text`
      - `is_correct`
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    if not questions:
        raise HTTPException(status_code=400, detail="This quiz has no questions.")

    # Fast lookup: question_id (str) → QuizQuestion
    question_map = {str(q.id): q for q in questions}

    score = 0
    total = len(questions)
    breakdown: List[QuestionResult] = []

    for answer in attempt.answers:
        q = question_map.get(str(answer.question_id))
        if not q:
            # Unknown question ID — skip gracefully
            continue

        selected = answer.selected_option.strip().upper()
        correct = q.correct_answer.strip().upper()
        is_correct = selected == correct

        if is_correct:
            score += 1

        # Persist answer to DB for history / analytics
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
                options=_build_options(q),
                selected_option=selected,
                selected_option_text=_option_text(q, selected),
                correct_option=correct,
                correct_option_text=_option_text(q, correct),
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
