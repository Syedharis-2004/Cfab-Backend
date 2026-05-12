import json
from pathlib import Path
from typing import List, Dict
from app.utils.logger import logger

def fill_powerbi_template(template_path: Path, visuals_config: List[Dict], output_path: Path):
    """
    Reads an uploaded JSON template and injects visualization recommendations.
    """
    logger.info(f"Filling Power BI JSON template: {template_path}")
    try:
        # Load the template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # If it's a dict, we merge the visuals. If it's a list, we might append or replace.
        # Based on the example format provided by the user: {"visuals": [...]}
        if isinstance(template_data, dict):
            if "visuals" not in template_data:
                template_data["visuals"] = []
            template_data["visuals"].extend(visuals_config)
        else:
            # Fallback for other structures
            template_data = {"original_template": template_data, "visuals": visuals_config}
            
        # Save the filled template
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=4)
            
        logger.info(f"Power BI template filled and saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error filling Power BI template: {str(e)}")
        raise e
