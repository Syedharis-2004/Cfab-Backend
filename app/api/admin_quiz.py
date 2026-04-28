from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import json
import csv
import io
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizAdminResponse, QuestionAdminResponse, QuizCreateRequest
from app.models.user import User
from app.services.pdf_parser import parse_quiz_pdf, PDF_SUPPORT

router = APIRouter(prefix="/admin/quiz", tags=["admin-quiz"])

async def _get_admin_quiz_response(quiz: Quiz) -> QuizAdminResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizAdminResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[QuestionAdminResponse(
            id=q.id,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct=q.correct_answer
        ) for q in questions]
    )

@router.post("", response_model=QuizAdminResponse)
async def create_quiz(quiz_in: QuizCreateRequest, current_admin: User = Depends(get_admin_user)):
    """
    Create a quiz with questions using option_a, b, c, d format.
    """
    quiz = Quiz(
        title=quiz_in.title,
        created_by=current_admin.id
    )
    await quiz.insert()

    for q in quiz_in.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct_answer=q.correct_answer.upper()
        )
        await question.insert()

    # Reuse existing response helper (might need update if QuizAdminResponse uses options list)
    return await _get_admin_quiz_response(quiz)


@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Deleted"}
