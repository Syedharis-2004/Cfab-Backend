import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.assignment import Assignment, AssignmentType
from app.models.coding_assignment import CodingAssignment
from app.models.test_case import TestCase
from app.models.user import User
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.models.submission import Submission
from app.core.config import settings

CODING_ASSIGNMENTS = [
    {
        "title": "Sum of Two Numbers",
        "description": "Write a program that reads two integers and prints their sum.",
        "function_name": "solve",
        "starter_code": "def solve(a, b):\n    # return a + b\n    pass",
        "language": "python",
        "test_cases": [
            {"input": "[3, 5]",  "expected_output": "8",  "is_hidden": False},
            {"input": "[10, 20]","expected_output": "30", "is_hidden": False},
        ],
    },
    {
        "title": "Reverse a String",
        "description": "Return the string reversed.",
        "function_name": "reverse_it",
        "starter_code": "def reverse_it(s):\n    pass",
        "language": "python",
        "test_cases": [
            {"input": "'hello'", "expected_output": "'olleh'", "is_hidden": False},
        ],
    },
]

async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[User, Assignment, CodingAssignment, Quiz, QuizQuestion, UserAnswer, TestCase, Submission],
    )

    # Clear old coding assignments to avoid structure mismatch
    # We delete from Assignment, CodingAssignment, and TestCase
    coding_ids = [a.id for a in await Assignment.find(Assignment.assignment_type == AssignmentType.CODING).to_list()]
    for aid in coding_ids:
        await TestCase.find(TestCase.assignment_id == aid).delete()
        await CodingAssignment.find(CodingAssignment.assignment_id == aid).delete()
        await Assignment.find(Assignment.id == aid).delete()
    
    print("Cleared existing coding assignments.")

    for data in CODING_ASSIGNMENTS:
        # 1. Main catalog entry
        assignment = Assignment(
            title=data["title"],
            assignment_type=AssignmentType.CODING,
        )
        await assignment.insert()

        # 2. Detailed metadata
        coding_meta = CodingAssignment(
            assignment_id=assignment.id,
            title=data["title"],
            description=data["description"],
            function_name=data["function_name"],
            starter_code=data["starter_code"],
            language=data["language"],
        )
        await coding_meta.insert()

        # 3. Test cases
        for tc_data in data["test_cases"]:
            tc = TestCase(
                assignment_id=assignment.id,
                input=tc_data["input"],
                expected_output=tc_data["expected_output"],
                is_hidden=tc_data["is_hidden"],
            )
            await tc.insert()

        print(f"  [OK] Seeded: {data['title']}")

    print("\nSeeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
