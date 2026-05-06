import re
import logging
from typing import List, Dict, Any

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not PDF_SUPPORT:
        raise ImportError("pdfplumber is not installed.")
    import io
    text_pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    return "\n".join(text_pages)

def parse_mcq_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Returns a list of dicts with keys: question, options (List[str]), correct (str), correct_label (str)
    """
    questions = []
    
    # Split the text by questions using regex: look for "1.", "2.", etc.
    blocks = re.split(r'\n(?=\d+[.)]\s)', "\n" + text)
    
    for block in blocks:
        block = block.strip()
        if not block: continue
        
        # Match question number and text
        q_match = re.search(r'^(\d+)[.)]\s+(.*?)(?=\s*[A-Da-d][.)]|\Z)', block, re.DOTALL)
        if not q_match:
            continue
            
        q_text = q_match.group(2).strip()
        
        # Extract options
        options_matches = re.findall(r'([A-Da-d])[.)]\s*(.*?)(?=\s*[A-Da-d][.)]|\s*Answer:|\Z)', block, re.DOTALL | re.IGNORECASE)
        
        options_dict = {m[0].upper(): m[1].strip() for m in options_matches}
        
        # Extract answer
        ans_match = re.search(r'Answer\s*[:\-]\s*([A-Da-d])', block, re.IGNORECASE)
        correct_label = ans_match.group(1).upper() if ans_match else "A"
        
        if q_text and options_dict:
            labels = sorted(options_dict.keys())
            options_list = [options_dict[l] for l in labels]
            correct_text = options_dict.get(correct_label, "")
            
            questions.append({
                "question": q_text,
                "options": options_list,
                "correct": correct_text,
                "correct_label": correct_label
            })
            
    return questions

def parse_quiz_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("PDF is empty or non-parseable.")
    questions = parse_mcq_from_text(text)
    if not questions:
        raise ValueError("No MCQs found. Required format: 1. Q? A) Opt Answer: A")
    return questions
