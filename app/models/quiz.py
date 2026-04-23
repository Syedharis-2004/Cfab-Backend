from beanie import Document

class Quiz(Document):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str # 'a', 'b', 'c', or 'd'

    class Settings:
        name = "quizzes"

