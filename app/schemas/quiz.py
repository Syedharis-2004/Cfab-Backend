from pydantic import BaseModel, validator
from typing import List, Optional
from beanie import PydanticObjectId


# ─────────────────────────────────────────────────────────────────────────────
#  Admin-facing  (include correct answer)
# ─────────────────────────────────────────────────────────────────────────────

class QuestionCreate(BaseModel):
    """Schema used when an admin creates / uploads questions."""
    question: str
    options: List[str]   # ["var", "let", "const", "All of the above"]
    correct: str         # Must be the EXACT text of one of the options

    @validator("correct")
    def correct_must_be_in_options(cls, v, values):
        options = values.get("options", [])
        if v not in options:
            raise ValueError(
                f"'correct' must exactly match one of the options. "
                f"Got '{v}' but options are {options}"
            )
        return v

    @validator("options")
    def at_least_two_options(cls, v):
        if len(v) < 2:
            raise ValueError("A question must have at least 2 options.")
        return v


class QuestionAdminResponse(BaseModel):
    """Question data returned to admins — includes the correct answer."""
    id: Optional[PydanticObjectId] = None
    question: str
    options: List[str]
    correct: str


# ─────────────────────────────────────────────────────────────────────────────
#  Quiz-level admin schemas
# ─────────────────────────────────────────────────────────────────────────────

class QuizBase(BaseModel):
    title: str


class QuizCreate(QuizBase):
    questions: List[QuestionCreate]


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None


class QuizAdminResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionAdminResponse] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
#  User-facing  (correct answer hidden)
# ─────────────────────────────────────────────────────────────────────────────

class QuestionResponse(BaseModel):
    """Question data returned to regular users — NO correct answer."""
    id: Optional[PydanticObjectId] = None
    question: str
    options: List[str]   # ["var", "let", "const", "All of the above"]


class QuizResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
#  Submission
# ─────────────────────────────────────────────────────────────────────────────

class AnswerAttempt(BaseModel):
    question_id: str
    selected_option: str   # The EXACT text of the option the user picked


class QuizAttempt(BaseModel):
    answers: List[AnswerAttempt]


# ─────────────────────────────────────────────────────────────────────────────
#  Result  (returned after submission)
# ─────────────────────────────────────────────────────────────────────────────

class QuestionResult(BaseModel):
    """Per-question result breakdown."""
    question_id: str
    question_text: str
    options: List[str]
    selected_option: str    # What the user picked
    correct_option: str     # What was correct
    is_correct: bool


class QuizResult(BaseModel):
    """Full result returned after quiz submission."""
    score: int            # Number of correct answers
    total: int            # Total questions in quiz
    percentage: float     # Score as percentage
    passed: bool          # True if >= 50%
    breakdown: List[QuestionResult]
