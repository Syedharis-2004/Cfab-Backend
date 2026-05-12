import pandas as pd
from typing import List, Dict
from pathlib import Path
from app.utils.logger import logger

def fill_response_template(answers: List[Dict], template_file_bytes: bytes, template_filename: str, output_path: Path) -> str:
    logger.info(f"Filling response template: {template_filename}")
    
    try:
        # Load template
        ext = template_filename.split('.')[-1].lower()
        if ext == 'csv':
            import io
            df = pd.read_csv(io.BytesIO(template_file_bytes))
        elif ext in ['xlsx', 'xls']:
            import io
            df = pd.read_excel(io.BytesIO(template_file_bytes))
        else:
            # If no template provided or wrong format, create a new one
            df = pd.DataFrame(answers)
            df.to_excel(output_path, index=False)
            return str(output_path)

        # Simple logic: assume template has 'Question' and 'Answer' columns or we append
        # This is highly dependent on the user's template format.
        # For now, we'll create a new DataFrame from answers if template mapping fails.
        
        results_df = pd.DataFrame(answers)
        
        if ext == 'csv':
            results_df.to_csv(output_path, index=False)
        else:
            results_df.to_excel(output_path, index=False)
            
        logger.info(f"Response file saved to: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Error filling template: {str(e)}")
        # Fallback to simple excel
        results_df = pd.DataFrame(answers)
        results_df.to_excel(output_path, index=False)
        return str(output_path)
