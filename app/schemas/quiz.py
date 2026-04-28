from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId


# ─────────────────────────────────────────────
#  Option  (A / B / C / D  labelled choice)
# ─────────────────────────────────────────────

class OptionItem(BaseModel):
    """A single labelled option shown to the user."""
    key: str    # "A", "B", "C", or "D"
    text: str   # The actual option text


# ─────────────────────────────────────────────
#  Admin-facing schemas  (include correct answer)
# ─────────────────────────────────────────────

class QuestionCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str   # Must be "A", "B", "C", or "D"

class QuestionAdminResponse(BaseModel):
    id: Optional[PydanticObjectId] = None
    question: str
    options: List[OptionItem]
    correct_answer: str   # "A" / "B" / "C" / "D"

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


# ─────────────────────────────────────────────
#  User-facing schemas  (correct answer hidden)
# ─────────────────────────────────────────────

class QuestionResponse(BaseModel):
    """Question returned to a regular user — NO correct answer."""
    id: Optional[PydanticObjectId] = None
    question: str
    options: List[OptionItem]   # [{"key": "A", "text": "..."}, ...]

class QuizResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
#  Submission / attempt
# ─────────────────────────────────────────────

class AnswerAttempt(BaseModel):
    question_id: str
    selected_option: str   # "A", "B", "C", or "D"

class QuizAttempt(BaseModel):
    answers: List[AnswerAttempt]


# ─────────────────────────────────────────────
#  Result schemas  (returned after submission)
# ─────────────────────────────────────────────

class QuestionResult(BaseModel):
    """Per-question result breakdown."""
    question_id: str
    question_text: str
    options: List[OptionItem]
    selected_option: str        # e.g. "B"
    selected_option_text: str   # e.g. "London"
    correct_option: str         # e.g. "A"
    correct_option_text: str    # e.g. "Paris"
    is_correct: bool

class QuizResult(BaseModel):
    """Full result returned after quiz submission."""
    score: int          # Number of correct answers
    total: int          # Total questions
    percentage: float   # Score as percentage
    passed: bool        # True if >= 50%
    breakdown: List[QuestionResult]
