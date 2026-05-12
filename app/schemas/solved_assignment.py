from pydantic import BaseModel
from typing import Optional

class PythonModeResponse(BaseModel):
    success: bool
    response_file: str
    summary_file: str
    questions_processed: int

class PowerBIModeResponse(BaseModel):
    success: bool
    config_file: str
    visuals_generated: int

class AssignmentHistoryItem(BaseModel):
    id: str
    mode: str
    status: str
    created_at: str
    questions_processed: int
