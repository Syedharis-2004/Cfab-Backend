import asyncio
import os
from app.core.database import init_db
from app.models.user import User
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.core.security import get_password_hash

async def seed():
    # Initialize Beanie
    await init_db()
    
    # Check if data already exists
    if await User.find_one():
        print("Database already seeded.")
        return

    # Seed User
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    await user.insert()
    
    # Seed Assignment
    assignment = Assignment(
        title="Python Basics Practice",
        pdf_path="uploads/assignments/sample_practice.pdf"
    )
    await assignment.insert()
    
    # Seed Quizzes
    quizzes = [
        Quiz(
            question="What is the output of print(2**3)?",
            option_a="6",
            option_b="8",
            option_c="9",
            option_d="5",
            correct_answer="b"
        ),
        Quiz(
            question="Which of these is a mutable data type in Python?",
            option_a="Tuple",
            option_b="String",
            option_c="List",
            option_d="Integer",
            correct_answer="c"
        ),
        Quiz(
            question="What keyword is used to define a function in Python?",
            option_a="fun",
            option_b="function",
            option_c="def",
            option_d="define",
            correct_answer="c"
        )
    ]
    await Quiz.insert_many(quizzes)
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    # Ensure upload directory exists
    if not os.path.exists("uploads/assignments"):
        os.makedirs("uploads/assignments")
    
    asyncio.run(seed())
