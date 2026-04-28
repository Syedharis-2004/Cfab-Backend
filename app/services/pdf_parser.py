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
    Returns a list of dicts with keys: question, options (List[str]), correct (str)
    """
    questions = []
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    current_question = None
    current_options = {} # Label -> Text
    current_answer_label = None

    question_pattern = re.compile(r'^(\d+)[.)]\s+(.+)$')
    option_pattern = re.compile(r'^([A-Da-d])[).\-\s]\s*(.+)$')
    answer_pattern = re.compile(r'^[Aa]nswer\s*[:\-]\s*([A-Da-d])', re.IGNORECASE)

    def save_question():
        nonlocal current_question, current_options, current_answer_label
        if current_question and len(current_options) >= 2 and current_answer_label:
            labels = sorted(current_options.keys())
            options_list = [current_options[l] for l in labels]
            correct_text = current_options.get(current_answer_label, "")
            
            questions.append({
                "question": current_question,
                "options": options_list,
                "correct": correct_text
            })
        current_question = None
        current_options = {}
        current_answer_label = None

    for line in lines:
        q_match = question_pattern.match(line)
        opt_match = option_pattern.match(line)
        ans_match = answer_pattern.match(line)

        if q_match:
            save_question()
            current_question = q_match.group(2).strip()
        elif opt_match and current_question:
            current_options[opt_match.group(1).upper()] = opt_match.group(2).strip()
        elif ans_match and current_question:
            current_answer_label = ans_match.group(1).upper()
        elif current_question and not opt_match and not ans_match:
            if not current_options:
                current_question += " " + line

    save_question()
    return questions

def parse_quiz_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("PDF is empty or non-parseable.")
    questions = parse_mcq_from_text(text)
    if not questions:
        raise ValueError("No MCQs found. Required format: 1. Q? A) Opt Answer: A")
    return questions
