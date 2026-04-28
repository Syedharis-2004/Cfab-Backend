from beanie import Document, PydanticObjectId
from typing import Optional

class UserAnswer(Document):
    user_id: PydanticObjectId
    quiz_id: PydanticObjectId
    question_id: PydanticObjectId          # Which question was answered
    selected_answer: str                    # What the user chose (A/B/C/D)
    correct_answer: str                     # What the correct answer was
    is_correct: bool = False               # Was the user's answer right?

    class Settings:
        name = "user_answers"
