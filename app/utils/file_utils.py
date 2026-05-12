import os
import shutil
import uuid
from pathlib import Path

OUTPUT_BASE_DIR = Path("outputs")

def get_user_assignment_dir(user_id: str, assignment_id: str) -> Path:
    path = OUTPUT_BASE_DIR / user_id / assignment_id
    path.mkdir(parents=True, exist_ok=True)
    return path

async def save_upload_file(upload_file, dest_path: Path):
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

def generate_id() -> str:
    return str(uuid.uuid4())
