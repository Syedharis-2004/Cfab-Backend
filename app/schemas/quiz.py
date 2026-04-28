from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId

class QuestionBase(BaseModel):
    id: Optional[PydanticObjectId] = None
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuestionCreate(QuestionBase):
    correct_answer: str

class QuestionResponse(QuestionBase):
    pass

class QuestionAdminResponse(QuestionBase):
    correct_answer: str

class QuizBase(BaseModel):
    title: str

class QuizCreate(QuizBase):
    questions: List[QuestionCreate]

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None

class QuizResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

class QuizAdminResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionAdminResponse] = []

    class Config:
        from_attributes = True

class AnswerAttempt(BaseModel):
    question_id: str
    selected_answer: str  # Must be A, B, C, or D

class QuizAttempt(BaseModel):
    answers: List[AnswerAttempt]

# --- Detailed Result Schemas ---

class QuestionResult(BaseModel):
    """Per-question breakdown returned after quiz submission."""
    question_id: str
    question_text: str
    your_answer: str           # What user chose
    correct_answer: str        # What was correct
    is_correct: bool           # Did user get it right?
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizResult(BaseModel):
    """Full result returned after submitting a quiz."""
    score: int                        # Number of correct answers
    total: int                        # Total number of questions
    percentage: float                 # Score percentage
    passed: bool                      # True if >= 50%
    breakdown: List[QuestionResult]   # Per-question detail
