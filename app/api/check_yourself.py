from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.api.auth import get_current_user
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.schemas.assignment import AssignmentListItem
from app.schemas.quiz import QuizResponse
from app.models.user import User

router = APIRouter(prefix="/check-yourself", tags=["check-yourself"])

@router.get("", response_model=Dict[str, Any])
async def get_check_yourself_data(current_user: User = Depends(get_current_user)):
    """
    Unified endpoint for the Check Yourself dashboard.
    Returns available assignments and quizzes.
    """
    assignments = await Assignment.find_all().to_list()
    quizzes = await Quiz.find_all().to_list()
    
    return {
        "assignments": [
            AssignmentListItem(
                id=a.id,
                title=a.title,
                assignment_type=a.assignment_type,
                created_at=a.created_at
            ) for a in assignments
        ],
        "quizzes": [
            {
                "id": str(q.id),
                "title": q.title,
                "question_count": len(q.questions)
            } for q in quizzes
        ]
    }
