import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_quiz_pdf_upload():
    print("\n--- Testing Quiz PDF Upload ---")
    test_filename = "python_quiz.pdf"
    if not os.path.exists(test_filename):
        print(f"Error: {test_filename} not found.")
        return None

    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        data = {"title": "Verification Quiz"}
        response = requests.post(f"{BASE_URL}/admin/quiz/upload-pdf", data=data, files=files)
    
    if response.status_code == 200:
        res_json = response.json()
        quiz_id = res_json['id']
        print(f"[SUCCESS] Quiz Uploaded: {res_json['title']} (ID: {quiz_id})")
        print(f"Extracted {len(res_json['questions'])} questions.")
        for q in res_json['questions']:
            print(f" - Q: {q['question']} | Ans: {q['correct']}")
        return quiz_id
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")
        return None

def test_practice_assignment_upload():
    print("\n--- Testing Practice Assignment PDF Upload ---")
    test_filename = "python_quiz.pdf" # Reusing same PDF for simplicity
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        data = {"title": "Practice PDF Assignment", "description": "A test PDF assignment"}
        response = requests.post(f"{BASE_URL}/assignments/upload", data=data, files=files)
    
    if response.status_code == 200:
        res_json = response.json()
        assignment_id = res_json['id']
        print(f"[SUCCESS] Assignment Uploaded: {res_json['title']} (ID: {assignment_id})")
        return assignment_id
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")
        return None

def test_delete_quiz(quiz_id):
    print(f"\n--- Testing Delete Quiz (ID: {quiz_id}) ---")
    response = requests.delete(f"{BASE_URL}/admin/quiz/{quiz_id}")
    if response.status_code == 200:
        print("[SUCCESS] Quiz deleted.")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")

def test_delete_assignment(assignment_id):
    print(f"\n--- Testing Delete Assignment (ID: {assignment_id}) ---")
    response = requests.delete(f"{BASE_URL}/assignments/{assignment_id}")
    if response.status_code == 200:
        print("[SUCCESS] Assignment deleted.")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(BASE_URL)
    except:
        print(f"Error: Server is not running at {BASE_URL}. Please start it first.")
        exit(1)

    q_id = test_quiz_pdf_upload()
    a_id = test_practice_assignment_upload()

    if q_id: test_delete_quiz(q_id)
    if a_id: test_delete_assignment(a_id)
