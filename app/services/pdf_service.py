import pdfplumber
import io
import re
from typing import List
from app.utils.logger import logger

def extract_questions_from_pdf(file_bytes: bytes) -> List[str]:
    logger.info("Starting PDF question extraction")
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            logger.warning("PDF extraction returned no text")
            return []

        # Simple question detection: lines ending with '?' or starting with numbers
        lines = text.split('\n')
        questions = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Logic: Match lines ending with '?' or starting with "Q1.", "1.", etc.
            if line.endswith('?') or re.match(r'^(Q|Question\s*)?\d+[\.\)\:]', line, re.I):
                questions.append(line)
        
        logger.info(f"Extracted {len(questions)} questions from PDF")
        return questions
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise e
