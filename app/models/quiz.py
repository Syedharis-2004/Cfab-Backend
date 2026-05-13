from beanie import Document, PydanticObjectId
from typing import List, Optional


class Quiz(Document):
    title: str
    created_by: Optional[PydanticObjectId] = None

    class Settings:
        name = "quizzes"


class QuizQuestion(Document):
    quiz_id: Optional[PydanticObjectId] = None
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str      # A, B, C, or D

    class Settings:
        name = "quiz_questions"
