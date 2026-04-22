from pydantic import BaseModel
from typing import List

class QuizBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizCreate(QuizBase):
    correct_answer: str

class Quiz(QuizBase):
    id: int

    class Config:
        from_attributes = True

class QuizSubmission(BaseModel):
    quiz_id: int
    selected_answer: str

class QuizResult(BaseModel):
    score: int
    total: int
