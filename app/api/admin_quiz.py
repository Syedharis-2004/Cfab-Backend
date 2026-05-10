from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
import traceback
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


@router.post("/upload", response_model=QuizAdminResponse)
@router.post("/upload-pdf", response_model=QuizAdminResponse)
async def upload_quiz_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_admin: User = Depends(get_admin_user)
):
    """
    Upload a Quiz PDF and automatically extract questions and answers.
    """
    logger.info(f"--- Quiz Upload Started: {title} (File: {file.filename}) ---")
    
    try:
        # 1. Validation
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        if not PDF_SUPPORT:
            logger.error("PDF parsing service (pdfplumber) is not configured.")
            raise HTTPException(status_code=500, detail="PDF parsing service is not configured. Please install pdfplumber.")

        # 2. File Reading
        logger.info("Reading file content...")
        try:
            content = await file.read()
            if not content:
                logger.warning("Uploaded file is empty.")
                raise ValueError("The uploaded file is empty.")
            logger.info(f"Read {len(content)} bytes successfully.")
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Could not read file: {str(e)}")

        # 3. PDF Parsing
        logger.info("Starting PDF parsing...")
        try:
            extracted_questions = parse_quiz_pdf(content)
            logger.info(f"Successfully extracted {len(extracted_questions)} questions from PDF.")
        except ValueError as ve:
            logger.warning(f"PDF content validation failed: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Unexpected PDF Parsing error: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF structure: {str(e)}")

        # 4. Admin Context Validation
        if not current_admin or not getattr(current_admin, "id", None):
            logger.error("Admin user ID is missing from context.")
            raise HTTPException(status_code=401, detail="Invalid admin session: Missing user ID")

        # 5. Database Insertion (Quiz)
        logger.info("Saving Quiz to database...")
        try:
            quiz = Quiz(
                title=title,
                created_by=current_admin.id
            )
            await quiz.insert()
            logger.info(f"Quiz created in DB with ID: {quiz.id}")
        except Exception as e:
            logger.error(f"Database error while saving Quiz: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database error while saving quiz: {str(e)}")

        # 6. Database Insertion (Questions)
        logger.info(f"Saving {len(extracted_questions)} questions to database...")
        try:
            for i, q_data in enumerate(extracted_questions):
                options = q_data.get("options", [])
                correct_label = q_data.get("correct_label", "A").upper()
                
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question=q_data["question"],
                    option_a=options[0] if len(options) > 0 else "N/A",
                    option_b=options[1] if len(options) > 1 else "N/A",
                    option_c=options[2] if len(options) > 2 else "N/A",
                    option_d=options[3] if len(options) > 3 else "N/A",
                    correct_answer=correct_label
                )
                await question.insert()
            logger.info("All questions saved successfully.")
        except Exception as e:
            logger.error(f"Database error while saving questions: {str(e)}\n{traceback.format_exc()}")
            # Cleanup: Delete the partial quiz if questions fail? (Optional)
            raise HTTPException(status_code=500, detail=f"Database error while saving questions: {str(e)}")

        # 7. Response Generation
        logger.info("Generating response...")
        try:
            response = await _get_admin_quiz_response(quiz)
            logger.info("--- Quiz Upload Completed Successfully ---")
            return response
        except Exception as e:
            logger.error(f"Response validation error: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Data saved but failed to generate response schema.")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.critical(f"UNHANDLED EXCEPTION in upload_quiz_pdf: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )


@router.delete("/{id}")
async def delete_quiz(id: str, current_admin: User = Depends(get_admin_user)):
    quiz = await Quiz.get(id)
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    await QuizQuestion.find(QuizQuestion.quiz_id == quiz.id).delete()
    await quiz.delete()
    return {"message": "Deleted"}
