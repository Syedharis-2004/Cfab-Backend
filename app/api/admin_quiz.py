from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import json
import csv
import io
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizCreate, QuizAdminResponse, QuizUpdate, QuestionCreate, QuestionAdminResponse
from app.models.user import User

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
            correct_answer=q.correct_answer
        ) for q in questions]
    )

@router.post("/manual", response_model=QuizAdminResponse)
async def create_quiz_manual(quiz_in: QuizCreate, current_admin: User = Depends(get_admin_user)):
    quiz = Quiz(
        title=quiz_in.title,
        created_by=current_admin.id
    )
    await quiz.insert()
    
    for q in quiz_in.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            **q.dict()
        )
        await question.insert()
        
    return await _get_admin_quiz_response(quiz)

@router.post("/upload", response_model=QuizAdminResponse)
async def upload_quiz(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    questions_data = []
    content = await file.read()
    
    if file.filename.endswith('.json'):
        try:
            questions_data = json.loads(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
            
    elif file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                questions_data.append(row)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use JSON or CSV.")

    quiz = Quiz(
        title=title,
        created_by=current_admin.id
    )
    await quiz.insert()
    
    for q_data in questions_data:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question=q_data['question'],
            option_a=q_data['option_a'],
            option_b=q_data['option_b'],
            option_c=q_data['option_c'],
            option_d=q_data['option_d'],
            correct_answer=q_data['correct_answer']
        )
        await question.insert()
        
    return await _get_admin_quiz_response(quiz)

@router.put("/{id}", response_model=QuizAdminResponse)
async def update_quiz(id: str, quiz_in: QuizUpdate, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz_in.title:
        quiz.title = quiz_in.title
        await quiz.save()
        
    if quiz_in.questions is not None:
        # Delete existing questions and replace them
        await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
        for q in quiz_in.questions:
            question = QuizQuestion(
                quiz_id=quiz.id,
                **q.dict()
            )
            await question.insert()
    
    return await _get_admin_quiz_response(quiz)

@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Delete associated questions
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Quiz deleted successfully"}
