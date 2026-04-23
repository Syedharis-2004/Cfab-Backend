from beanie import Document, PydanticObjectId
from typing import Optional


class TestCase(Document):
    """Standalone test case document linked to a coding assignment."""
    assignment_id: PydanticObjectId
    input: str
    expected_output: str
    is_hidden: bool = False      # hidden = not shown to users, still evaluated

    class Settings:
        name = "test_cases"
