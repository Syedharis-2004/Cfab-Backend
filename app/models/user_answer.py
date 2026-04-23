from beanie import Document, PydanticObjectId

class UserAnswer(Document):
    user_id: PydanticObjectId
    quiz_id: PydanticObjectId
    selected_answer: str

    class Settings:
        name = "user_answers"
