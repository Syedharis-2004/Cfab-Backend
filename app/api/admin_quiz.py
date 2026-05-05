from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
import csv
import io
import logging
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizAdminResponse, QuestionAdminResponse, QuizCreateRequest
from app.models.user import User
from app.services.pdf_parser import parse_quiz_pdf, PDF_SUPPORT

logger = logging.getLogger(__name__)

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


@router.post("/upload-pdf", response_model=QuizAdminResponse)
async def upload_quiz_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    """
    Upload a Quiz PDF and automatically extract questions and answers.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not PDF_SUPPORT:
        raise HTTPException(status_code=500, detail="PDF parsing service is not configured.")

    try:
        content = await file.read()
        extracted_questions = parse_quiz_pdf(content)
    except Exception as e:
        logger.error(f"PDF Parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    if not extracted_questions:
        raise HTTPException(status_code=400, detail="No questions could be extracted from the PDF.")

    # Create the quiz
    quiz = Quiz(
        title=title,
        created_by=current_admin.id
    )
    await quiz.insert()

    # Save extracted questions
    for q_data in extracted_questions:
        # q_data looks like {"question": "...", "options": ["...", "..."], "correct": "..."}
        # We need to map options to A, B, C, D
        options = q_data["options"]
        
        # Determine which option is correct
        correct_label = q_data.get("correct_label", "A").upper()
        
        question = QuizQuestion(
            quiz_id=quiz.id,
            question=q_data["question"],
            option_a=options[0] if len(options) > 0 else "",
            option_b=options[1] if len(options) > 1 else "",
            option_c=options[2] if len(options) > 2 else "",
            option_d=options[3] if len(options) > 3 else "",
            correct_answer=correct_label
        )
        await question.insert()

    return await _get_admin_quiz_response(quiz)


@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Deleted"}
