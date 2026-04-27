import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def upload_assignment_pdf():
    print("Uploading python_assignment.pdf to Assignment section...")
    test_filename = "python_assignment.pdf"
    if not os.path.exists(test_filename):
        print(f"Error: {test_filename} not found.")
        return

    params = {"title": "Python Assignment"}
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/assignments/upload", data=params, files=files)
    
    if response.status_code == 200:
        print(f"[SUCCESS] Assignment PDF Uploaded: {response.json()['title']}")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")

def upload_quiz_pdf():
    print("Uploading python_quiz.pdf to Assignment section (as PDF Quiz)...")
    test_filename = "python_quiz.pdf"
    if not os.path.exists(test_filename):
        print(f"Error: {test_filename} not found.")
        return

    params = {"title": "Python Quiz (PDF)"}
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/assignments/upload", data=params, files=files)
    
    if response.status_code == 200:
        print(f"[SUCCESS] Quiz PDF Uploaded: {response.json()['title']}")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")

if __name__ == "__main__":
    upload_assignment_pdf()
    upload_quiz_pdf()
