from datetime import datetime, timezone
from typing import Optional, Dict
from beanie import Document, Indexed
from pydantic import Field

class SolvedAssignment(Document):
    user_id: Indexed(str)
    mode: str  # "python" or "powerbi"
    pdf_file: str
    dataset_file: str
    response_template: Optional[str] = None
    generated_files: Dict[str, str] = {}  # {"notebook": "...", "powerbi_response": "...", "summary": "..."}
    status: str = "pending"  # "pending", "completed", "failed"
    questions_processed: int = 0
    visuals_generated: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "solved_assignments"
