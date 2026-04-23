from pydantic import BaseModel
from typing import List
from beanie import PydanticObjectId

class QuizBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizCreate(QuizBase):
    correct_answer: str

class Quiz(QuizBase):
    id: PydanticObjectId

    class Config:
        from_attributes = True

class QuizSubmission(BaseModel):
    quiz_id: PydanticObjectId
    selected_answer: str

class QuizResult(BaseModel):
    score: int
    total: int
