from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.schemas.quiz import Quiz as QuizSchema, QuizSubmission, QuizResult

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("", response_model=List[QuizSchema])
def get_quiz_questions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Quiz).all()

@router.post("/submit", response_model=QuizResult)
def submit_quiz(submissions: List[QuizSubmission], db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    score = 0
    total = len(submissions)
    
    for submission in submissions:
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
        if not quiz:
            continue
        
        # Save user answer
        db_answer = UserAnswer(
            user_id=current_user.id,
            quiz_id=submission.quiz_id,
            selected_answer=submission.selected_answer
        )
        db.add(db_answer)
        
        if submission.selected_answer.lower() == quiz.correct_answer.lower():
            score += 1
            
    db.commit()
    return {"score": score, "total": total}

