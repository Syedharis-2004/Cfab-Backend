from datetime import datetime
from typing import Optional
from beanie import Document, Indexed

class SolvedAssignment(Document):
    user_id: Indexed(str)
    mode: str  # "python" or "powerbi"
    pdf_file: str
    dataset_file: str
    response_file: Optional[str] = None
    summary_file: Optional[str] = None
    config_file: Optional[str] = None
    status: str = "pending"  # "pending", "completed", "failed"
    questions_processed: int = 0
    visuals_generated: int = 0
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "solved_assignments"
