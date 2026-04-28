from beanie import Document, PydanticObjectId
from typing import List


class Quiz(Document):
    title: str
    created_by: PydanticObjectId

    class Settings:
        name = "quizzes"


class QuizQuestion(Document):
    quiz_id: PydanticObjectId
    question: str
    options: List[str]       # e.g. ["var", "let", "const", "All of the above"]
    correct_answer: str      # exact text of the correct option, e.g. "const"

    class Settings:
        name = "quiz_questions"
