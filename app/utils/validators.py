from fastapi import HTTPException, UploadFile
import os

ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed.")
    
    # Check file size (optional, requires reading file)
    # file.file.seek(0, os.SEEK_END)
    # size = file.file.tell()
    # file.file.seek(0)
    # if size > MAX_FILE_SIZE:
    #     raise HTTPException(status_code=400, detail="File too large.")
