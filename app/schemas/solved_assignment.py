from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class PythonFiles(BaseModel):
    notebook: str
    summary: str

class PowerBIFiles(BaseModel):
    powerbi_response: str
    summary: str

class PythonDownloadUrls(BaseModel):
    notebook: str
    summary: str

class PowerBIDownloadUrls(BaseModel):
    powerbi_response: str
    summary: str

class PythonModeResponse(BaseModel):
    success: bool
    files: PythonFiles
    download_urls: PythonDownloadUrls
    questions_processed: int

class PowerBIModeResponse(BaseModel):
    success: bool
    files: PowerBIFiles
    download_urls: PowerBIDownloadUrls
    visuals_generated: int

class AssignmentHistoryItem(BaseModel):
    id: str
    mode: str
    status: str
    created_at: datetime
    questions_processed: int
    visuals_generated: int
