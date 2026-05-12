from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Dict
import os
from datetime import datetime
from pathlib import Path

from app.api.auth import get_current_user
from app.models.solved_assignment import SolvedAssignment
from app.schemas.solved_assignment import (
    PythonModeResponse, PowerBIModeResponse, 
    PythonFiles, PowerBIFiles, 
    PythonDownloadUrls, PowerBIDownloadUrls
)
from app.services import (
    pdf_service, dataset_service, llm_service, 
    notebook_template_service, powerbi_template_service, 
    summary_service
)
from app.utils.validators import validate_file
from app.utils.file_utils import get_user_assignment_dir, save_upload_file, generate_id
from app.utils.logger import logger

router = APIRouter(prefix="/api/solved-assignment", tags=["Solved Assignment"])

@router.post("/process-python", response_model=PythonModeResponse)
async def process_python_mode(
    pdf_file: UploadFile = File(...),
    dataset_file: UploadFile = File(...),
    response_template: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    logger.info(f"Python Mode (Template) started for user {current_user.id}")
    
    validate_file(pdf_file)
    validate_file(dataset_file)
    if not response_template.filename.endswith(".ipynb"):
        raise HTTPException(status_code=400, detail="Response template must be a .ipynb file.")
    
    assignment_id = generate_id()
    output_dir = get_user_assignment_dir(str(current_user.id), assignment_id)
    
    pdf_path = output_dir / pdf_file.filename
    dataset_path = output_dir / dataset_file.filename
    template_path = output_dir / response_template.filename
    
    await save_upload_file(pdf_file, pdf_path)
    await save_upload_file(dataset_file, dataset_path)
    await save_upload_file(response_template, template_path)
    
    # 2. Extract
    pdf_bytes = pdf_path.read_bytes()
    questions = pdf_service.extract_questions_from_pdf(pdf_bytes)
    
    # 3. Load & Analyze
    dataset_bytes = dataset_path.read_bytes()
    df = dataset_service.load_dataset(dataset_bytes, dataset_file.filename)
    dataset_context = dataset_service.get_dataset_context(df)
    
    # 4. AI Answers
    answers_data = await llm_service.get_ai_answers(questions, dataset_context)
    
    # 5. Fill Template
    notebook_filename = "filled_assignment.ipynb"
    notebook_path = output_dir / notebook_filename
    notebook_template_service.fill_notebook_template(template_path, answers_data, notebook_path)
    
    # 6. Generate Detailed Summary
    summary_filename = summary_service.generate_detailed_summary(
        output_dir, "python", len(questions), list(df.columns), answers_data
    )
    
    # 7. MongoDB
    history = SolvedAssignment(
        user_id=str(current_user.id),
        mode="python",
        pdf_file=str(pdf_path),
        dataset_file=str(dataset_path),
        response_template=str(template_path),
        generated_files={
            "notebook": str(notebook_path),
            "summary": str(output_dir / summary_filename)
        },
        status="completed",
        questions_processed=len(questions),
        created_at=datetime.utcnow()
    )
    await history.insert()
    
    return PythonModeResponse(
        success=True,
        files=PythonFiles(
            notebook=str(notebook_path),
            summary=str(output_dir / summary_filename)
        ),
        download_urls=PythonDownloadUrls(
            notebook=f"/api/solved-assignment/download/{notebook_filename}?uid={current_user.id}&aid={assignment_id}",
            summary=f"/api/solved-assignment/download/{summary_filename}?uid={current_user.id}&aid={assignment_id}"
        ),
        questions_processed=len(questions)
    )

@router.post("/process-powerbi", response_model=PowerBIModeResponse)
async def process_powerbi_mode(
    pdf_file: UploadFile = File(...),
    dataset_file: UploadFile = File(...),
    response_template: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    logger.info(f"Power BI Mode (Template) started for user {current_user.id}")
    
    validate_file(pdf_file)
    validate_file(dataset_file)
    if not response_template.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Response template must be a .json file.")
    
    assignment_id = generate_id()
    output_dir = get_user_assignment_dir(str(current_user.id), assignment_id)
    
    pdf_path = output_dir / pdf_file.filename
    dataset_path = output_dir / dataset_file.filename
    template_path = output_dir / response_template.filename
    
    await save_upload_file(pdf_file, pdf_path)
    await save_upload_file(dataset_file, dataset_path)
    await save_upload_file(response_template, template_path)
    
    # Extract
    pdf_bytes = pdf_path.read_bytes()
    questions = pdf_service.extract_questions_from_pdf(pdf_bytes)
    
    # Load
    dataset_bytes = dataset_path.read_bytes()
    df = dataset_service.load_dataset(dataset_bytes, dataset_file.filename)
    dataset_context = dataset_service.get_dataset_context(df)
    
    # Visuals
    visuals_config = await llm_service.get_visualization_recommendations(questions, dataset_context)
    
    # 5. Fill Template
    powerbi_filename = "filled_powerbi_response.json"
    powerbi_path = output_dir / powerbi_filename
    powerbi_template_service.fill_powerbi_template(template_path, visuals_config, powerbi_path)
    
    # 6. Summary
    summary_filename = summary_service.generate_detailed_summary(
        output_dir, "powerbi", len(questions), list(df.columns), visuals_config
    )
    
    # 7. MongoDB
    history = SolvedAssignment(
        user_id=str(current_user.id),
        mode="powerbi",
        pdf_file=str(pdf_path),
        dataset_file=str(dataset_path),
        response_template=str(template_path),
        generated_files={
            "powerbi_response": str(powerbi_path),
            "summary": str(output_dir / summary_filename)
        },
        status="completed",
        visuals_generated=len(visuals_config),
        created_at=datetime.utcnow()
    )
    await history.insert()
    
    return PowerBIModeResponse(
        success=True,
        files=PowerBIFiles(
            powerbi_response=str(powerbi_path),
            summary=str(output_dir / summary_filename)
        ),
        download_urls=PowerBIDownloadUrls(
            powerbi_response=f"/api/solved-assignment/download/{powerbi_filename}?uid={current_user.id}&aid={assignment_id}",
            summary=f"/api/solved-assignment/download/{summary_filename}?uid={current_user.id}&aid={assignment_id}"
        ),
        visuals_generated=len(visuals_config)
    )

@router.get("/download/{file_name}")
async def download_file(
    file_name: str,
    uid: str,
    aid: str,
    current_user = Depends(get_current_user)
):
    """
    Secure download endpoint for assignment outputs.
    """
    # Security: Ensure user can only download their own files
    if str(current_user.id) != uid:
        raise HTTPException(status_code=403, detail="Forbidden: Access denied.")
    
    file_path = Path("outputs") / uid / aid / file_name
    
    if not file_path.exists():
        logger.error(f"Download failed: File not found at {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
        
    logger.info(f"Downloading file: {file_name} for user {uid}")
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )
