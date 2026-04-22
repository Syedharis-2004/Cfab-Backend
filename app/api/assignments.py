from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from typing import List

from app.api.auth import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.models.assignment import Assignment
from app.schemas.assignment import Assignment as AssignmentSchema

router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.get("", response_model=List[AssignmentSchema])
def get_assignments(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Assignment).all()

@router.get("/search", response_model=List[AssignmentSchema])
def search_assignments(title: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Search assignments by title. 'title' is a required query parameter."""
    return db.query(Assignment).filter(Assignment.title.contains(title)).all()


@router.get("/{assignment_id}")
def get_assignment_file(assignment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if not os.path.exists(assignment.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on server")
    
    return FileResponse(assignment.pdf_path, media_type="application/pdf", filename=os.path.basename(assignment.pdf_path))

# Admin upload endpoint (for testing and setup)
@router.post("/upload", response_model=AssignmentSchema)
def upload_assignment(title: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR)
    
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_assignment = Assignment(title=title, pdf_path=file_path)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment
