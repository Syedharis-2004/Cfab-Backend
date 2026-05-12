from pathlib import Path
import json
from typing import List, Dict
from app.utils.logger import logger

def save_summary_file(output_dir: Path, data: Dict) -> str:
    logger.info("Generating summary.txt")
    summary_path = output_dir / "summary.txt"
    
    with open(summary_path, "w") as f:
        f.write("Solved Assignment Summary\n")
        f.write("==========================\n\n")
        f.write(f"Mode: {data.get('mode', 'N/A')}\n")
        f.write(f"Status: {data.get('status', 'N/A')}\n")
        f.write(f"Questions Processed: {data.get('questions_processed', 0)}\n")
        if 'visuals_generated' in data:
            f.write(f"Visuals Generated: {data.get('visuals_generated', 0)}\n")
        f.write(f"Timestamp: {data.get('timestamp', 'N/A')}\n\n")
        
        f.write("Files Generated:\n")
        for file in data.get('files', []):
            f.write(f"- {file}\n")
            
    return str(summary_path)

def save_config_file(output_dir: Path, config: List[Dict]) -> str:
    logger.info("Generating visualization_config.json")
    config_path = output_dir / "visualization_config.json"
    
    with (config_path).open("w") as f:
        json.dump({"visuals": config}, f, indent=4)
        
    return str(config_path)
