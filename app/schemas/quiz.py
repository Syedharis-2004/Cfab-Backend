from pydantic import BaseModel, validator
from typing import List, Optional
from beanie import PydanticObjectId


# ─────────────────────────────────────────────────────────────────────────────
#  Admin-facing  (include correct answer)
# ─────────────────────────────────────────────────────────────────────────────

class QuestionCreateRequest(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str

    @validator("correct_answer")
    def validate_correct_answer(cls, v):
        if v.upper() not in ["A", "B", "C", "D"]:
            raise ValueError("correct_answer must be one of A, B, C, or D")
        return v.upper()

class QuizCreateRequest(BaseModel):
    title: str
    questions: List[QuestionCreateRequest]

class QuestionAdminResponse(BaseModel):
    """Question data returned to admins — includes the correct answer."""
    id: Optional[PydanticObjectId] = None
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct: str

class QuizBase(BaseModel):
    title: str

class QuizAdminResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionAdminResponse] = []

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    """Question data returned to regular users — NO correct answer."""
    id: Optional[PydanticObjectId] = None
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

class AnswerSubmitRequest(BaseModel):
    question_id: str
    selected_answer: str

    @validator("selected_answer")
    def validate_selected(cls, v):
        if v.upper() not in ["A", "B", "C", "D"]:
            raise ValueError("selected answer must be one of A, B, C, or D")
        return v.upper()

class QuizSubmitRequest(BaseModel):
    quiz_id: Optional[PydanticObjectId] = None
    answers: List[AnswerSubmitRequest]
