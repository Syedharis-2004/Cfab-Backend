from pydantic import BaseModel
from datetime import datetime

class AssignmentBase(BaseModel):
    title: str

class AssignmentCreate(AssignmentBase):
    pdf_path: str

class Assignment(AssignmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
