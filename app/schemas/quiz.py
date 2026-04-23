from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId

class QuestionBase(BaseModel):
    id: str
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
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True

class QuizAdminResponse(QuizBase):
    id: PydanticObjectId
    questions: List[QuestionAdminResponse]

    class Config:
        from_attributes = True

class AnswerAttempt(BaseModel):
    question_id: str
    selected_answer: str

class QuizAttempt(BaseModel):
    answers: List[AnswerAttempt]

class QuizResult(BaseModel):
    score: int
    total: int
    percentage: float
