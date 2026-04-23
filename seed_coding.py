"""
seed_coding.py — Seed the database with sample coding assignments.

Run with:
    python seed_coding.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.assignment import Assignment, AssignmentType
from app.models.test_case import TestCase
from app.models.user import User
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.models.submission import Submission
from app.core.config import settings

CODING_ASSIGNMENTS = [
    {
        "title": "Sum of Two Numbers",
        "description": (
            "## Sum of Two Numbers\n\n"
            "Write a program that reads two integers from stdin (on the same line, space-separated) "
            "and prints their sum.\n\n"
            "**Input format:** Two space-separated integers `a` and `b`.\n\n"
            "**Output format:** A single integer — the sum of `a` and `b`.\n\n"
            "**Example:**\n"
            "```\n"
            "Input:  3 5\n"
            "Output: 8\n"
            "```"
        ),
        "starter_code": "a, b = map(int, input().split())\n# Write your solution here\n",
        "language": "python",
        "test_cases": [
            {"input": "3 5",  "expected_output": "8",  "is_hidden": False},
            {"input": "10 20","expected_output": "30", "is_hidden": False},
            {"input": "-1 1", "expected_output": "0",  "is_hidden": True},
            {"input": "0 0",  "expected_output": "0",  "is_hidden": True},
        ],
    },
    {
        "title": "Reverse a String",
        "description": (
            "## Reverse a String\n\n"
            "Read a single word from stdin and print it reversed.\n\n"
            "**Input:** A single string (no spaces).\n\n"
            "**Output:** The string reversed.\n\n"
            "**Example:**\n"
            "```\n"
            "Input:  hello\n"
            "Output: olleh\n"
            "```"
        ),
        "starter_code": "s = input()\n# Write your solution here\n",
        "language": "python",
        "test_cases": [
            {"input": "hello",   "expected_output": "olleh",   "is_hidden": False},
            {"input": "python",  "expected_output": "nohtyp",  "is_hidden": False},
            {"input": "racecar", "expected_output": "racecar", "is_hidden": True},
            {"input": "a",       "expected_output": "a",       "is_hidden": True},
        ],
    },
    {
        "title": "FizzBuzz",
        "description": (
            "## FizzBuzz\n\n"
            "Read an integer `n` from stdin. For each number from 1 to n:\n"
            "- Print `Fizz` if divisible by 3\n"
            "- Print `Buzz` if divisible by 5\n"
            "- Print `FizzBuzz` if divisible by both\n"
            "- Otherwise print the number\n\n"
            "**Input:** A single integer `n`.\n\n"
            "**Output:** n lines."
        ),
        "starter_code": "n = int(input())\nfor i in range(1, n + 1):\n    # Write your solution here\n    pass\n",
        "language": "python",
        "test_cases": [
            {
                "input": "5",
                "expected_output": "1\n2\nFizz\n4\nBuzz",
                "is_hidden": False,
            },
            {
                "input": "15",
                "expected_output": (
                    "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"
                ),
                "is_hidden": True,
            },
        ],
    },
]


async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[User, Assignment, Quiz, UserAnswer, TestCase, Submission],
    )

    for data in CODING_ASSIGNMENTS:
        # Avoid duplicates
        existing = await Assignment.find_one(
            {"title": data["title"], "assignment_type": AssignmentType.CODING}
        )
        if existing:
            print(f"  [SKIP] Already exists: {data['title']}")
            continue

        assignment = Assignment(
            title=data["title"],
            assignment_type=AssignmentType.CODING,
            description=data["description"],
            starter_code=data["starter_code"],
            language=data["language"],
        )
        await assignment.insert()

        for tc_data in data["test_cases"]:
            tc = TestCase(
                assignment_id=assignment.id,
                input=tc_data["input"],
                expected_output=tc_data["expected_output"],
                is_hidden=tc_data["is_hidden"],
            )
            await tc.insert()

        print(f"  [OK] Seeded: {data['title']} ({len(data['test_cases'])} test cases)")

    print("\nSeeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
