import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId
from app.models.user import User
from app.models.assignment import Assignment, AssignmentType
from app.models.coding_assignment import CodingAssignment
from app.models.test_case import TestCase
from app.models.quiz import Quiz, QuizQuestion
from app.core.security import get_password_hash
from app.core.config import settings

async def seed():
    print("Initializing database connection...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0] or "check_yourself"
    
    await init_beanie(
        database=client[db_name],
        document_models=[
            User,
            Assignment,
            CodingAssignment,
            TestCase,
            Quiz,
            QuizQuestion,
        ]
    )

    print("Cleaning up existing data...")
    await User.find_all().delete()
    await Assignment.find_all().delete()
    await CodingAssignment.find_all().delete()
    await TestCase.find_all().delete()
    await Quiz.find_all().delete()
    await QuizQuestion.find_all().delete()

    # 1. Seed Users
    print("Seeding users...")
    admin_user = User(
        name="Admin User",
        email="admin@cfab.com",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    await admin_user.insert()

    normal_user = User(
        name="Student User",
        email="student@cfab.com",
        hashed_password=get_password_hash("student123"),
        role="user"
    )
    await normal_user.insert()

    # 2. Seed PDF Assignments
    print("Seeding PDF assignments...")
    pdf_assignments = [
        Assignment(
            title="Python Fundamentals",
            description="Introduction to Python syntax and variables.",
            assignment_type=AssignmentType.PDF,
            file_path="uploads/assignments/python_basics.pdf"
        ),
        Assignment(
            title="Data Structures in Python",
            description="Learn about Lists, Tuples, and Dictionaries.",
            assignment_type=AssignmentType.PDF,
            file_path="uploads/assignments/data_structures.pdf"
        )
    ]
    for assignment in pdf_assignments:
        await assignment.insert()

    # 3. Seed Coding Assignments
    print("Seeding coding assignments...")
    coding_data = [
        {
            "title": "Sum of Two Numbers",
            "description": "Write a function `solve(a, b)` that returns the sum of two numbers.",
            "function_name": "solve",
            "starter_code": "def solve(a, b):\n    # Your code here\n    return a + b",
            "language": "python",
            "test_cases": [
                {"input": "[3, 5]", "expected_output": "8", "is_hidden": False},
                {"input": "[-1, 1]", "expected_output": "0", "is_hidden": False},
                {"input": "[100, 200]", "expected_output": "300", "is_hidden": True}
            ]
        },
        {
            "title": "Factorial Calculation",
            "description": "Write a function `factorial(n)` that returns the factorial of a non-negative integer n.",
            "function_name": "factorial",
            "starter_code": "def factorial(n):\n    # Your code here\n    if n == 0: return 1\n    return n * factorial(n-1)",
            "language": "python",
            "test_cases": [
                {"input": "[5]", "expected_output": "120", "is_hidden": False},
                {"input": "[0]", "expected_output": "1", "is_hidden": False},
                {"input": "[10]", "expected_output": "3628800", "is_hidden": True}
            ]
        }
    ]

    for data in coding_data:
        assignment = Assignment(
            title=data["title"],
            description=data["description"],
            assignment_type=AssignmentType.CODING
        )
        await assignment.insert()

        coding_meta = CodingAssignment(
            assignment_id=assignment.id,
            title=data["title"],
            description=data["description"],
            function_name=data["function_name"],
            starter_code=data["starter_code"],
            language=data["language"]
        )
        await coding_meta.insert()

        for tc_data in data["test_cases"]:
            tc = TestCase(
                assignment_id=assignment.id,
                input=tc_data["input"],
                expected_output=tc_data["expected_output"],
                is_hidden=tc_data["is_hidden"]
            )
            await tc.insert()

    # 4. Seed Quizzes
    print("Seeding quizzes...")
    quiz = Quiz(
        title="Python Basics Quiz",
        created_by=admin_user.id
    )
    await quiz.insert()

    quiz_questions = [
        QuizQuestion(
            quiz_id=quiz.id,
            question="What is the correct extension of a Python file?",
            option_a=".pyth",
            option_b=".pt",
            option_c=".py",
            option_d=".pyt",
            correct_answer="C"
        ),
        QuizQuestion(
            quiz_id=quiz.id,
            question="Which of the following is used to define a block of code in Python?",
            option_a="Brackets",
            option_b="Indentation",
            option_c="Parentheses",
            option_d="Semicolons",
            correct_answer="B"
        ),
        QuizQuestion(
            quiz_id=quiz.id,
            question="Which keyword is used for a function in Python?",
            option_a="function",
            option_b="def",
            option_c="fun",
            option_d="define",
            correct_answer="B"
        )
    ]
    for q in quiz_questions:
        await q.insert()

    print("\nDatabase seeded successfully!")
    print(f"Admin: admin@cfab.com / admin123")
    print(f"Student: student@cfab.com / student123")

if __name__ == "__main__":
    # Ensure uploads directory exists
    os.makedirs("uploads/assignments", exist_ok=True)
    asyncio.run(seed())
