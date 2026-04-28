from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import json
import csv
import io
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizCreate, QuizAdminResponse, QuizUpdate, QuestionAdminResponse
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
            options=q.options,
            correct=q.correct_answer
        ) for q in questions]
    )

@router.post("/manual", response_model=QuizAdminResponse)
async def create_quiz_manual(quiz_in: QuizCreate, current_admin: User = Depends(get_admin_user)):
    """
    Admin: Manually create a quiz.
    Questions use 'options' (list) and 'correct' (text).
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
            options=q.options,
            correct_answer=q.correct
        )
        await question.insert()
        
    return await _get_admin_quiz_response(quiz)

@router.post("/upload", response_model=QuizAdminResponse)
async def upload_quiz(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    """
    Admin: Bulk upload quiz questions.
    JSON/CSV must follow the new format: options as list/columns, correct as text.
    """
    questions_data = []
    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith('.json'):
        try:
            questions_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    elif filename.endswith('.csv'):
        # For CSV, we assume columns: question, options (comma separated), correct
        try:
            stream = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                row['options'] = [o.strip() for o in row['options'].split(',')]
                questions_data.append(row)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

    elif filename.endswith('.pdf'):
        if not PDF_SUPPORT:
            raise HTTPException(status_code=501, detail="PDF support not available.")
        questions_data = parse_quiz_pdf(content)

    else:
        raise HTTPException(status_code=400, detail="Unsupported format.")

    quiz = Quiz(
        title=title,
        created_by=current_admin.id
    )
    await quiz.insert()
    
    for q_data in questions_data:
        # Map to model fields
        question = QuizQuestion(
            quiz_id=quiz.id,
            question=q_data['question'],
            options=q_data.get('options') or [q_data['option_a'], q_data['option_b'], q_data['option_c'], q_data['option_d']],
            correct_answer=q_data.get('correct') or q_data.get('correct_answer')
        )
        # If it was an old format upload (A/B/C/D), we try to resolve it
        if not q_data.get('options') and 'correct_answer' in q_data:
            mapping = {"A": q_data['option_a'], "B": q_data['option_b'], "C": q_data['option_c'], "D": q_data['option_d']}
            question.correct_answer = mapping.get(q_data['correct_answer'].upper(), q_data['correct_answer'])

        await question.insert()
        
    return await _get_admin_quiz_response(quiz)

@router.put("/{id}", response_model=QuizAdminResponse)
async def update_quiz(id: str, quiz_in: QuizUpdate, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz_in.title:
        quiz.title = quiz_in.title
        await quiz.save()
        
    if quiz_in.questions is not None:
        await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
        for q in quiz_in.questions:
            await QuizQuestion(
                quiz_id=quiz.id,
                question=q.question,
                options=q.options,
                correct_answer=q.correct
            ).insert()
    
    return await _get_admin_quiz_response(quiz)

@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Deleted"}
