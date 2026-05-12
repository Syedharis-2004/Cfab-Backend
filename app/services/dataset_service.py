import pandas as pd
import io
from typing import Tuple, Dict, Any
from app.utils.logger import logger

def load_dataset(file_bytes: bytes, filename: str) -> pd.DataFrame:
    logger.info(f"Loading dataset: {filename}")
    ext = filename.split('.')[-1].lower()
    
    try:
        if ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Basic preprocessing
        df.dropna(how='all', inplace=True)
        logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise e

def get_dataset_context(df: pd.DataFrame) -> str:
    """Returns a string representation of the dataset for LLM context."""
    columns = df.columns.tolist()
    sample = df.head(10).to_string()
    summary = df.describe(include='all').to_string()
    
    context = f"Columns: {', '.join(columns)}\n\n"
    context += f"Data Sample (first 10 rows):\n{sample}\n\n"
    context += f"Data Summary:\n{summary}"
    return context
