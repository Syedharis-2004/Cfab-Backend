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
    # Sampling for large datasets
    sample_size = min(len(df), 50)
    sample = df.sample(sample_size).to_string() if len(df) > 50 else df.to_string()
    
    col_types = df.dtypes.to_dict()
    col_types_str = ", ".join([f"{k} ({v})" for k, v in col_types.items()])
    
    context = f"Columns & Types: {col_types_str}\n\n"
    context += f"Total Rows: {len(df)}\n\n"
    context += f"Data Sample ({sample_size} rows):\n{sample}\n\n"
    
    # Summary of numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        context += f"Numerical Summary:\n{df[numeric_cols].describe().to_string()}"
        
    return context
