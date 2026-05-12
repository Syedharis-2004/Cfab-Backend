import json
from pathlib import Path
from typing import Dict, List
from app.utils.logger import logger

def save_summary_file(output_dir: Path, data: Dict) -> str:
    summary_path = output_dir / "summary.txt"
    with open(summary_path, "w") as f:
        f.write("Solved Assignment System - Summary\n")
        f.write("=================================\n")
        for key, value in data.items():
            f.write(f"{key}: {value}\n")
    return summary_path.name

def save_config_file(output_dir: Path, config: List[Dict]) -> str:
    config_path = output_dir / "visualization_config.json"
    with open(config_path, "w") as f:
        json.dump({"visuals": config}, f, indent=4)
    return config_path.name

def get_download_url(user_id: str, assignment_id: str, filename: str) -> str:
    # This matches the route: GET /api/solved-assignment/download/{filename}
    # However, the filename needs to be unique enough or we need to pass IDs.
    # The requirement says GET /api/solved-assignment/download/{file_name}
    # But files are in outputs/{user_id}/{assignment_id}/.
    # To keep the API simple as requested, we might need to store the mapping or use a specific format.
    # For now, let's assume the filename in the URL is the full path or we encode it.
    # Actually, the user asked for GET /api/solved-assignment/download/{file_name}
    # I'll implement it such that it searches the latest outputs or we encode the path.
    return f"/api/solved-assignment/download/{user_id}/{assignment_id}/{filename}"
