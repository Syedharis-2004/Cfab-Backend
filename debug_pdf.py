import sys
import os
sys.path.append(os.getcwd())
from app.services.pdf_parser import extract_text_from_pdf

def debug_pdf():
    test_filename = "python_quiz.pdf"
    if not os.path.exists(test_filename):
        print("File not found")
        return
    
    with open(test_filename, "rb") as f:
        content = f.read()
    
    text = extract_text_from_pdf(content)
    print("--- Extracted Text ---")
    print(text)
    print("----------------------")

if __name__ == "__main__":
    debug_pdf()
