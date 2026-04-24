from beanie import Document, PydanticObjectId
from typing import Optional

class CodingAssignment(Document):
    """
    Detailed metadata for a coding assignment.
    Linked to the main Assignment via shared ID or title.
    """
    assignment_id: PydanticObjectId
    title: str
    description: str
    function_name: str
    starter_code: Optional[str] = None
    language: Optional[str] = "python"

    class Settings:
        name = "coding_assignments"
