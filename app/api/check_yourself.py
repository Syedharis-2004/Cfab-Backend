from fastapi import APIRouter
from typing import List, Dict, Any
from app.models.assignment import Assignment
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.assignment import AssignmentListItem
from app.utils.serializer import serialize_dict

router = APIRouter(prefix="/check-yourself", tags=["check-yourself"])

@router.get("", response_model=Dict[str, Any])
async def get_check_yourself_data():
    """
    Unified endpoint for the Check Yourself dashboard.
    Returns available assignments and quizzes.
    """
    assignments = await Assignment.find_all().to_list()
    quizzes = await Quiz.find_all().to_list()
    
    quiz_list = []
    for q in quizzes:
        count = await QuizQuestion.find(QuizQuestion.quiz_id == q.id).count()
        quiz_list.append({
            "id": str(q.id),
            "title": q.title,
            "question_count": count
        })
    
    return serialize_dict({
        "assignments": assignments,
        "quizzes": quiz_list
    })
