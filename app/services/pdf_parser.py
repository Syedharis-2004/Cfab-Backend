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
    
    logger.info(f"Parsing MCQ text (length: {len(text)})")
    
    # Pre-process: simplify whitespace but preserve newlines
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Split the text by questions using regex: look for "1.", "2.", "Q1.", etc. at the start of a line
    # Supporting: 1., 1), Q1., Question 1:
    blocks = re.split(r'\n\s*(?:Q(?:uestion)?\s*)?\d+[\.\)\:]\s*', "\n" + text)
    
    logger.info(f"Split text into {len(blocks)} potential blocks")
    
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block: continue
        
        logger.info(f"Processing block {i}: {block!r}")
        
        # 1. Extract Question Text
        # Find everything until the first option A) or 1)
        q_match = re.search(r'^(.*?)(?=\s*[A-Da-d][\.\)]\s+|\s*Answer:|\Z)', block, re.DOTALL)
        if not q_match or not q_match.group(1).strip():
            continue
            
        q_text = q_match.group(1).strip()
        
        # 2. Extract Options
        # Match "A) text" or "A. text"
        options_matches = re.findall(r'([A-D])[\.\)]\s*(.*?)(?=\s*[A-D][\.\)]\s+|\s*Answer:|\Z)', block, re.DOTALL | re.IGNORECASE)
        
        options_dict = {m[0].upper(): m[1].strip() for m in options_matches}
        
        # 3. Extract Answer
        # Match "Answer: A" or "Answer-A" or "Correct Answer: A"
        ans_match = re.search(r'(?:Correct\s+)?Answer\s*[:\-\s]\s*([A-D])', block, re.IGNORECASE)
        correct_label = ans_match.group(1).upper() if ans_match else None
        
        if q_text and len(options_dict) >= 2:
            # We need at least A and B to call it a question
            labels = ["A", "B", "C", "D"]
            options_list = [options_dict.get(l, "N/A") for l in labels]
            
            # If no answer found in block, default to A or skip? Let's skip if no answer for strictness
            if not correct_label:
                logger.warning(f"No answer found for question: {q_text[:50]}...")
                continue

            correct_text = options_dict.get(correct_label, "N/A")
            
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
