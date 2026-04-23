from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import json
import csv
import io
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, Question
from app.schemas.quiz import QuizCreate, QuizAdminResponse, QuizUpdate, QuestionCreate
from app.models.user import User

router = APIRouter(prefix="/admin/quiz", tags=["admin-quiz"])

@router.post("/manual", response_model=QuizAdminResponse)
async def create_quiz_manual(quiz_in: QuizCreate, current_admin: User = Depends(get_admin_user)):
    quiz = Quiz(
        title=quiz_in.title,
        created_by=current_admin.id,
        questions=[Question(**q.dict()) for q in quiz_in.questions]
    )
    await quiz.insert()
    return quiz

@router.post("/upload", response_model=QuizAdminResponse)
async def upload_quiz(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    questions = []
    content = await file.read()
    
    if file.filename.endswith('.json'):
        try:
            data = json.loads(content)
            for q in data:
                questions.append(Question(**q))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
            
    elif file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                questions.append(Question(
                    id=row['id'],
                    question=row['question'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_answer=row['correct_answer']
                ))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use JSON or CSV.")

    quiz = Quiz(
        title=title,
        created_by=current_admin.id,
        questions=questions
    )
    await quiz.insert()
    return quiz

@router.put("/{id}", response_model=QuizAdminResponse)
async def update_quiz(id: str, quiz_in: QuizUpdate, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    update_data = quiz_in.dict(exclude_unset=True)
    if 'questions' in update_data:
        update_data['questions'] = [Question(**q.dict()) if hasattr(q, 'dict') else Question(**q) for q in update_data['questions']]
    
    await quiz.update({"$set": update_data})
    return quiz

@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    await quiz.delete()
    return {"message": "Quiz deleted successfully"}
