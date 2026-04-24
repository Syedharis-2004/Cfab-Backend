from beanie import Document, PydanticObjectId
from typing import List, Optional

class Quiz(Document):
    title: str
    created_by: PydanticObjectId

    class Settings:
        name = "quizzes"

class QuizQuestion(Document):
    quiz_id: PydanticObjectId
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str # 'A', 'B', 'C', or 'D'

    class Settings:
        name = "quiz_questions"
