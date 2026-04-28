from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import json
import csv
import io
from app.api.auth import get_admin_user
from app.models.quiz import Quiz, QuizQuestion
from app.schemas.quiz import QuizCreate, QuizAdminResponse, QuizUpdate, QuestionCreate, QuestionAdminResponse, OptionItem
from app.models.user import User
from app.services.pdf_parser import parse_quiz_pdf, PDF_SUPPORT

router = APIRouter(prefix="/admin/quiz", tags=["admin-quiz"])

def _build_options(q: QuizQuestion) -> List[OptionItem]:
    return [
        OptionItem(key="A", text=q.option_a),
        OptionItem(key="B", text=q.option_b),
        OptionItem(key="C", text=q.option_c),
        OptionItem(key="D", text=q.option_d),
    ]

async def _get_admin_quiz_response(quiz: Quiz) -> QuizAdminResponse:
    questions = await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).to_list()
    return QuizAdminResponse(
        id=quiz.id,
        title=quiz.title,
        questions=[QuestionAdminResponse(
            id=q.id,
            question=q.question,
            options=_build_options(q),
            correct_answer=q.correct_answer
        ) for q in questions]
    )

@router.post("/manual", response_model=QuizAdminResponse)
async def create_quiz_manual(quiz_in: QuizCreate, current_admin: User = Depends(get_admin_user)):
    """
    Admin: Manually create a quiz by providing the full JSON structure including all questions and answers.
    """
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
    """
    Admin: Bulk upload quiz questions using a JSON, CSV, or PDF file.
    
    **Supported Formats:**
    
    - **JSON**: List of question objects with fields: question, option_a, option_b, option_c, option_d, correct_answer
    - **CSV**: Columns: question, option_a, option_b, option_c, option_d, correct_answer
    - **PDF**: Structured MCQ format (see below)
    
    **PDF Format Required:**
    ```
    1. Question text here?
    A) Option A text
    B) Option B text
    C) Option C text
    D) Option D text
    Answer: A
    
    2. Next question?
    ...
    ```
    """
    questions_data = []
    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith('.json'):
        try:
            questions_data = json.loads(content)
            if not isinstance(questions_data, list):
                raise HTTPException(status_code=400, detail="JSON must be a list of question objects.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

    elif filename.endswith('.csv'):
        try:
            stream = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                questions_data.append(dict(row))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")

    elif filename.endswith('.pdf'):
        if not PDF_SUPPORT:
            raise HTTPException(
                status_code=501,
                detail="PDF parsing is not available. The pdfplumber library is not installed."
            )
        try:
            questions_data = parse_quiz_pdf(content)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a JSON, CSV, or PDF file."
        )

    if not questions_data:
        raise HTTPException(status_code=400, detail="No questions found in the uploaded file.")

    # Validate required fields in all questions
    required_fields = {"question", "option_a", "option_b", "option_c", "option_d", "correct_answer"}
    for i, q_data in enumerate(questions_data):
        missing = required_fields - set(q_data.keys())
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Question #{i+1} is missing required fields: {', '.join(missing)}"
            )

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
            correct_answer=q_data['correct_answer'].upper()
        )
        await question.insert()
        
    return await _get_admin_quiz_response(quiz)

@router.put("/{id}", response_model=QuizAdminResponse)
async def update_quiz(id: str, quiz_in: QuizUpdate, current_admin: User = Depends(get_admin_user)):
    """
    Admin: Update an existing quiz's title or replace its entire question bank.
    """
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
    """
    Admin: Permanently delete a quiz and all its associated questions.
    """
    quiz = await Quiz.get(id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Delete associated questions
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Quiz deleted successfully"}
