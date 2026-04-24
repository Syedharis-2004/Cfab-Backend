from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.auth import get_current_user
from app.models.quiz import Quiz, QuizQuestion
from app.models.user_answer import UserAnswer
from app.schemas.quiz import QuizResponse, QuizAttempt, QuizResult, QuestionResponse
from app.models.user import User

router = APIRouter(prefix="/quiz", tags=["quiz"])

async def _get_quiz_response(quiz: Quiz) -> QuizResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[QuestionResponse(
            id=q.id,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d
        ) for q in questions]
    )

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(current_user: User = Depends(get_current_user)):
    quizzes = await Quiz.find_all().to_list()
    return [await _get_quiz_response(q) for q in quizzes]

@router.get("/{id}", response_model=QuizResponse)
async def get_quiz(id: str, current_user: User = Depends(get_current_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return await _get_quiz_response(quiz)

@router.post("/{id}/submit", response_model=QuizResult)
async def submit_quiz(id: str, attempt: QuizAttempt, current_user: User = Depends(get_current_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    if not questions:
         raise HTTPException(status_code=400, detail="Quiz has no questions")

    score = 0
    total = len(questions)
    
    # Map questions for easier lookup
    question_map = {str(q.id): q.correct_answer.upper() for q in questions}
    
    for answer in attempt.answers:
        correct_val = question_map.get(str(answer.question_id))
        if correct_val and answer.selected_answer.upper() == correct_val:
            score += 1
        
        # Save individual answers as per DB design: UserAnswers: id, user_id, quiz_id, selected_answer
        # Note: The DB design lists selected_answer, which might be per question. 
        # Requirement says UserAnswers: id, user_id, quiz_id, selected_answer. 
        # Usually this implies per question if it's many-to-one with Quiz.
        # I'll store them for record.
        ua = UserAnswer(
            user_id=current_user.id,
            quiz_id=quiz.id,
            selected_answer=answer.selected_answer
        )
        await ua.insert()
    
    percentage = (score / total * 100) if total > 0 else 0
    
    return {
        "score": score,
        "total": total,
        "percentage": round(percentage, 2)
    }
