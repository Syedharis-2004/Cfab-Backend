from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
import os
from datetime import datetime

from app.api.auth import get_current_user
from app.models.solved_assignment import SolvedAssignment
from app.schemas.solved_assignment import PythonModeResponse, PowerBIModeResponse
from app.services import (
    pdf_service, dataset_service, llm_service, 
    powerbi_service, response_service, output_service
)
from app.utils.validators import validate_file
from app.utils.file_utils import get_user_assignment_dir, save_upload_file, generate_id
from app.utils.logger import logger

router = APIRouter(prefix="/api/solved-assignment", tags=["Solved Assignment"])

@router.post("/process-python", response_model=PythonModeResponse)
async def process_python_mode(
    pdf_file: UploadFile = File(...),
    dataset_file: UploadFile = File(...),
    response_file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    logger.info(f"Python Mode started for user {current_user.id}")
    
    # 1. Validate files
    validate_file(pdf_file)
    validate_file(dataset_file)
    validate_file(response_file)
    
    assignment_id = generate_id()
    output_dir = get_user_assignment_dir(str(current_user.id), assignment_id)
    
    # Save uploaded files
    pdf_path = output_dir / pdf_file.filename
    dataset_path = output_dir / dataset_file.filename
    template_path = output_dir / response_file.filename
    
    await save_upload_file(pdf_file, pdf_path)
    await save_upload_file(dataset_file, dataset_path)
    await save_upload_file(response_file, template_path)
    
    # 2. Extract questions from PDF
    pdf_bytes = pdf_path.read_bytes()
    questions = pdf_service.extract_questions_from_pdf(pdf_bytes)
    
    if not questions:
        raise HTTPException(status_code=400, detail="No questions found in PDF.")
    
    # 3. Load and Analyze dataset
    dataset_bytes = dataset_path.read_bytes()
    df = dataset_service.load_dataset(dataset_bytes, dataset_file.filename)
    dataset_context = dataset_service.get_dataset_context(df)
    
    # 4. Get AI answers
    answers = await llm_service.get_ai_answers(questions, dataset_context)
    
    # 5. Fill response template
    output_response_path = output_dir / f"solved_{response_file.filename}"
    template_bytes = template_path.read_bytes()
    final_response_file = response_service.fill_response_template(
        answers, template_bytes, response_file.filename, output_response_path
    )
    
    # 6. Generate summary.txt
    summary_data = {
        "mode": "python",
        "status": "completed",
        "questions_processed": len(questions),
        "timestamp": datetime.utcnow().isoformat(),
        "files": [final_response_file, pdf_file.filename, dataset_file.filename]
    }
    summary_file = output_service.save_summary_file(output_dir, summary_data)
    
    # 7. Store history in MongoDB
    history = SolvedAssignment(
        user_id=str(current_user.id),
        mode="python",
        pdf_file=str(pdf_path),
        dataset_file=str(dataset_path),
        response_file=str(final_response_file),
        summary_file=str(summary_file),
        status="completed",
        questions_processed=len(questions),
        created_at=datetime.utcnow()
    )
    await history.insert()
    
    return PythonModeResponse(
        success=True,
        response_file=str(final_response_file),
        summary_file=str(summary_file),
        questions_processed=len(questions)
    )

@router.post("/process-powerbi", response_model=PowerBIModeResponse)
async def process_powerbi_mode(
    pdf_file: UploadFile = File(...),
    dataset_file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    logger.info(f"Power BI Mode started for user {current_user.id}")
    
    validate_file(pdf_file)
    validate_file(dataset_file)
    
    assignment_id = generate_id()
    output_dir = get_user_assignment_dir(str(current_user.id), assignment_id)
    
    pdf_path = output_dir / pdf_file.filename
    dataset_path = output_dir / dataset_file.filename
    
    await save_upload_file(pdf_file, pdf_path)
    await save_upload_file(dataset_file, dataset_path)
    
    # Extract questions
    pdf_bytes = pdf_path.read_bytes()
    questions = pdf_service.extract_questions_from_pdf(pdf_bytes)
    
    # Load dataset
    dataset_bytes = dataset_path.read_bytes()
    df = dataset_service.load_dataset(dataset_bytes, dataset_file.filename)
    dataset_context = dataset_service.get_dataset_context(df)
    
    # Generate Power BI config
    config = await powerbi_service.generate_powerbi_config(questions, dataset_context)
    config_file = output_service.save_config_file(output_dir, config)
    
    # History
    history = SolvedAssignment(
        user_id=str(current_user.id),
        mode="powerbi",
        pdf_file=str(pdf_path),
        dataset_file=str(dataset_path),
        config_file=str(config_file),
        status="completed",
        visuals_generated=len(config),
        created_at=datetime.utcnow()
    )
    await history.insert()
    
    return PowerBIModeResponse(
        success=True,
        config_file=str(config_file),
        visuals_generated=len(config)
    )
