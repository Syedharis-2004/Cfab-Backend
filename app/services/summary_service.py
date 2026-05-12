from pathlib import Path
from typing import List, Dict
from app.utils.logger import logger

def generate_detailed_summary(
    output_dir: Path,
    mode: str,
    questions_count: int,
    columns: List[str],
    results: List[Dict] = None
) -> str:
    """
    Generates a detailed summary.txt as per specific module requirements.
    """
    summary_path = output_dir / "summary.txt"
    logger.info(f"Generating detailed summary at {summary_path}")
    
    try:
        with open(summary_path, "w", encoding='utf-8') as f:
            f.write("Solved Assignment System - Detailed Summary\n")
            f.write("============================================\n\n")
            
            f.write("Tasks Performed:\n")
            f.write(f"- Mode: {mode.capitalize()}\n")
            f.write("- Loaded dataset successfully\n")
            f.write(f"- Extracted {questions_count} questions from PDF\n")
            f.write(f"- Analyzed {len(columns)} dataset columns\n")
            
            if mode == "python":
                f.write("- Performed advanced data analysis using Pandas\n")
                f.write("- Generated Python aggregation and visualization code\n")
                f.write("- Updated Jupyter Notebook response template\n")
            else:
                f.write("- Detected optimal visualization types\n")
                f.write("- Matched dataset columns to visual requirements\n")
                f.write("- Updated Power BI JSON response template\n")
            
            f.write("- Generated all downloadable response files\n\n")
            
            f.write("Dataset Information:\n")
            f.write(f"- Columns used: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}\n\n")
            
            f.write("AI-Generated Operations:\n")
            if results:
                for idx, res in enumerate(results[:5]): # Show first 5 operations
                    q = res.get('question', 'N/A')
                    f.write(f"  {idx+1}. Question: {q}\n")
                    if mode == "python":
                        f.write(f"     Code: {res.get('code', 'N/A')}\n")
                    else:
                        f.write(f"     Visual: {res.get('visual', 'N/A')}\n")
                
                if len(results) > 5:
                    f.write(f"  ... and {len(results) - 5} more questions.\n")
                    
        return summary_path.name
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary."
