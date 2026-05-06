import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_USER = "admin@example.com"
ADMIN_PASS = "admin123"

def get_admin_headers():
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": ADMIN_USER, "password": ADMIN_PASS})
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return None

def test_pdf_upload():
    print("\n--- Testing PDF Upload ---")
    headers = get_admin_headers()
    if not headers:
        print("[FAIL] Could not get admin headers.")
        return

    test_filename = "test_upload.pdf"
    with open(test_filename, "wb") as f:
        f.write(b"%PDF-1.4 test content")

    data = {"title": "Advanced Python Practice", "description": "Practice PDF for testing"}
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/assignments/upload", data=data, files=files, headers=headers)
    
    if response.status_code == 200:
        print(f"[SUCCESS] PDF Uploaded: {response.json()['title']}")
        return response.json()['id']
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")
        return None
    
    if os.path.exists(test_filename):
        os.remove(test_filename)

def test_coding_upload():
    print("\n--- Testing Coding Assignment Upload ---")
    headers = get_admin_headers()
    
    coding_data = {
        "title": "Power Calculation",
        "description": "Calculate a^b using solve(a, b)",
        "function_name": "solve",
        "test_cases": [
            {"input": "[2, 3]", "expected_output": "8", "is_hidden": False},
            {"input": "[10, 2]", "expected_output": "100", "is_hidden": True}
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/assignments/coding", json=coding_data, headers=headers)
    
    if resp.status_code == 200:
        assignment_id = resp.json()['id']
        print(f"[SUCCESS] Coding Assignment Created: {assignment_id}")
        return assignment_id
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")
        return None

def test_quiz_manual():
    print("\n--- Testing Manual Quiz Creation ---")
    headers = get_admin_headers()
    quiz_data = {
        "title": "Data Structures Quiz",
        "questions": [
            {
                "question": "Which is O(1) for access?",
                "option_a": "Linked List",
                "option_b": "Array",
                "option_c": "Binary Tree",
                "option_d": "Stack",
                "correct_answer": "B"
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/admin/quiz", json=quiz_data, headers=headers)
    if resp.status_code == 200:
        quiz_id = resp.json()['id']
        print(f"[SUCCESS] Quiz Created: {resp.json()['title']} (ID: {quiz_id})")
        return quiz_id
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")
        return None

def test_dashboard():
    print("\n--- Testing Check Yourself Dashboard ---")
    user_email = f"user_{int(time.time())}@dashboard.com"
    requests.post(f"{BASE_URL}/auth/register", json={"email": user_email, "name": "Dashboard User", "password": "password123"})
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": user_email, "password": "password123"})
    user_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    
    resp = requests.get(f"{BASE_URL}/check-yourself", headers=user_headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] Dashboard returned {len(data['assignments'])} assignments and {len(data['quizzes'])} quizzes.")
        return user_headers
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")
        return None

def test_quiz_submission(quiz_id, user_headers):
    if not quiz_id or not user_headers: return
    print("\n--- Testing Quiz Submission ---")
    
    # Get questions first to find the question ID
    resp = requests.get(f"{BASE_URL}/quiz/{quiz_id}", headers=user_headers)
    if resp.status_code != 200:
        print(f"[FAILED] Could not get quiz: {resp.text}")
        return
    
    quiz_data = resp.json()
    q_id = quiz_data['questions'][0]['id']
    
    submission = {
        "answers": [{"question_id": q_id, "selected_answer": "B"}]
    }
    
    resp = requests.post(f"{BASE_URL}/quiz/{quiz_id}/submit", json=submission, headers=user_headers)
    if resp.status_code == 200:
        print(f"[SUCCESS] Quiz submitted. Result: {resp.json()}")
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")

def test_coding_submission(assignment_id, user_headers):
    if not assignment_id or not user_headers: return
    print("\n--- Testing Coding Submission ---")
    
    submission = {
        "assignment_id": assignment_id,
        "code": "def solve(a, b): return a ** b",
        "language": "python"
    }
    
    resp = requests.post(f"{BASE_URL}/coding-assignments/submit", json=submission, headers=user_headers)
    if resp.status_code == 202:
        sub_id = resp.json()['id']
        print(f"[SUCCESS] Coding submission received. ID: {sub_id}")
        
        # Poll for status with multiple retries
        print("Polling for results...")
        for _ in range(5):
            time.sleep(2)
            resp = requests.get(f"{BASE_URL}/coding-assignments/submissions/{sub_id}", headers=user_headers)
            if resp.status_code == 200:
                status = resp.json()['status']
                print(f"Current status: {status}")
                if status != "pending" and status != "running":
                    print(f"[SUCCESS] Submission evaluated as: {status}")
                    return
            else:
                print(f"[FAILED] Could not poll status: {resp.text}")
                return
        print("[INFO] Submission still pending after 10s.")
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")

def test_search_and_download(pdf_id, user_headers):
    if not pdf_id or not user_headers: return
    print("\n--- Testing Search and Download ---")
    
    # Test search
    resp = requests.get(f"{BASE_URL}/assignments/search", params={"title": "Advanced"}, headers=user_headers)
    if resp.status_code == 200:
        results = resp.json()
        print(f"[SUCCESS] Search returned {len(results)} results.")
    else:
        print(f"[FAILED] Search failed: {resp.text}")

    # Test detail
    resp = requests.get(f"{BASE_URL}/assignments/{pdf_id}", headers=user_headers)
    if resp.status_code == 200:
        print(f"[SUCCESS] Retrieved assignment detail: {resp.json()['title']}")
    else:
        print(f"[FAILED] Detail failed: {resp.text}")

    # Test file download
    resp = requests.get(f"{BASE_URL}/assignments/{pdf_id}/file", headers=user_headers)
    if resp.status_code == 200:
        print(f"[SUCCESS] Downloaded file. Size: {len(resp.content)} bytes.")
    else:
        print(f"[FAILED] Download failed: {resp.text}")

if __name__ == "__main__":
    print("=== STARTING COMPREHENSIVE FEATURE TESTS ===")
    
    # Admin actions
    pdf_id = test_pdf_upload()
    coding_id = test_coding_upload()
    quiz_id = test_quiz_manual()
    
    # User actions
    user_headers = test_dashboard()
    
    if user_headers:
        test_quiz_submission(quiz_id, user_headers)
        test_search_and_download(pdf_id, user_headers)
        test_coding_submission(coding_id, user_headers)
    
    print("\n=== ALL TESTS COMPLETED ===")


