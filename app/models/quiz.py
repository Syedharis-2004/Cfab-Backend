from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    id: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str # 'a', 'b', 'c', or 'd'

class Quiz(Document):
    title: str
    created_by: PydanticObjectId
    questions: List[Question]

    class Settings:
        name = "quizzes"

