from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.auth import get_current_user
from app.models.quiz import Quiz
from app.models.user_answer import UserAnswer
from app.schemas.quiz import Quiz as QuizSchema, QuizSubmission, QuizResult

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("", response_model=List[QuizSchema])
async def get_quiz_questions(current_user = Depends(get_current_user)):
    return await Quiz.find_all().to_list()

@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submissions: List[QuizSubmission], current_user = Depends(get_current_user)):
    score = 0
    total = len(submissions)
    
    for submission in submissions:
        quiz = await Quiz.get(submission.quiz_id)
        if not quiz:
            continue
        
        # Save user answer
        db_answer = UserAnswer(
            user_id=current_user.id,
            quiz_id=submission.quiz_id,
            selected_answer=submission.selected_answer
        )
        await db_answer.insert()
        
        if submission.selected_answer.lower() == quiz.correct_answer.lower():
            score += 1
            
    return {"score": score, "total": total}

