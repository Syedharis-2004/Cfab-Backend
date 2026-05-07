import requests

BASE_URL = "http://127.0.0.1:8001/api"

def test_pdf_quiz_upload():
    test_filename = "python_quiz_with_answers.pdf"
    
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        data = {"title": "Python Basics PDF Quiz"}
        response = requests.post(f"{BASE_URL}/admin/quiz/upload", data=data, files=files)
    
    if response.status_code == 200:
        res_json = response.json()
        print(f"[SUCCESS] Quiz Uploaded: {res_json['title']}")
        print(f"Extracted {len(res_json['questions'])} questions.")
        for q in res_json['questions'][:2]: # print first 2
            print(f" - {q['question']}")
            print(f"   A) {q['option_a']}, B) {q['option_b']}, C) {q['option_c']}, D) {q['option_d']}")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_pdf_quiz_upload()
