"""
PDF Quiz Parser Service
=======================
Extracts MCQ (Multiple Choice Questions) from a PDF file.

Expected PDF Format:
--------------------
1. What is Python?
A) A snake
B) A programming language
C) A game
D) None of the above
Answer: B

2. Which keyword defines a function?
A) function
B) define
C) def
D) fun
Answer: C

Rules:
- Questions must start with a number followed by a period or closing paren (e.g., "1." or "1)")
- Options must be labeled A, B, C, D (with ), ., or - as separator)
- Correct answer line must start with "Answer:" (case-insensitive)
"""

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
    """Extract all text from a PDF file given its bytes."""
    if not PDF_SUPPORT:
        raise ImportError("pdfplumber is not installed. Add it to requirements.txt.")

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
    Parse MCQ questions from extracted PDF text.
    Returns a list of dicts with keys:
      question, option_a, option_b, option_c, option_d, correct_answer
    """
    questions = []

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]  # Remove empty lines

    current_question = None
    current_options = {}
    current_answer = None

    # Regex patterns
    question_pattern = re.compile(r'^(\d+)[.)]\s+(.+)$')
    option_pattern = re.compile(r'^([A-Da-d])[).\-\s]\s*(.+)$')
    answer_pattern = re.compile(r'^[Aa]nswer\s*[:\-]\s*([A-Da-d])', re.IGNORECASE)

    def save_question():
        """Save current question if it's complete."""
        if (current_question and
                all(k in current_options for k in ['A', 'B', 'C', 'D']) and
                current_answer):
            questions.append({
                "question": current_question,
                "option_a": current_options['A'],
                "option_b": current_options['B'],
                "option_c": current_options['C'],
                "option_d": current_options['D'],
                "correct_answer": current_answer.upper()
            })

    for line in lines:
        q_match = question_pattern.match(line)
        opt_match = option_pattern.match(line)
        ans_match = answer_pattern.match(line)

        if q_match:
            # Save previous question before starting a new one
            save_question()
            current_question = q_match.group(2).strip()
            current_options = {}
            current_answer = None

        elif opt_match and current_question:
            letter = opt_match.group(1).upper()
            text_val = opt_match.group(2).strip()
            current_options[letter] = text_val

        elif ans_match and current_question:
            current_answer = ans_match.group(1).upper()

        elif current_question and not opt_match and not ans_match:
            # This might be a continuation of the question text
            # Only append if we don't have options yet (multi-line question)
            if 'A' not in current_options:
                current_question += " " + line

    # Save the last question
    save_question()

    return questions


def parse_quiz_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Main entry point: Extract and parse MCQ questions from a PDF file.
    Returns a list of question dicts ready for database insertion.
    Raises ValueError if no questions could be parsed.
    """
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("PDF appears to be empty or contains only images (non-parseable text).")

    questions = parse_mcq_from_text(text)

    if not questions:
        raise ValueError(
            "Could not parse any MCQ questions from the PDF. "
            "Please ensure the PDF follows the required format:\n"
            "1. Question text\n"
            "A) Option A\nB) Option B\nC) Option C\nD) Option D\n"
            "Answer: A"
        )

    logger.info(f"Successfully parsed {len(questions)} questions from PDF.")
    return questions
