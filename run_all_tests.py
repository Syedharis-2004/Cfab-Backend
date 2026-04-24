import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000"
ADMIN_USER = "admin@example.com"
ADMIN_PASS = "admin123"

def get_admin_headers():
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": ADMIN_USER, "password": ADMIN_PASS})
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return None

def test_pdf_upload_with_params():
    print("\n--- Testing PDF Upload with Query Parameters ---")
    headers = get_admin_headers()
    if not headers:
        print("[FAIL] Could not get admin headers.")
        return

    test_filename = "test_upload.pdf"
    with open(test_filename, "wb") as f:
        f.write(b"%PDF-1.4 test content")

    params = {"title": "Advanced Python Practice"}
    with open(test_filename, "rb") as f:
        files = {"file": (test_filename, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/assignments/upload", params=params, files=files, headers=headers)
    
    if response.status_code == 200:
        print(f"[SUCCESS] PDF Uploaded: {response.json()['title']}")
    else:
        print(f"[FAILED] Status {response.status_code}: {response.text}")
    
    if os.path.exists(test_filename):
        os.remove(test_filename)

def test_coding_upload_with_params():
    print("\n--- Testing Coding Assignment Upload (JSON) ---")
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
    
    with open("temp_coding.json", "w") as f:
        json.dump(coding_data, f)
    
    with open("temp_coding.json", "rb") as f:
        files = {"file": ("temp_coding.json", f, "application/json")}
        resp = requests.post(f"{BASE_URL}/admin/coding-assignment/upload", files=files, headers=headers)
    
    if resp.status_code == 200:
        print(f"[SUCCESS] Coding Assignment Created: {resp.json()['assignment_id']}")
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")
    
    if os.path.exists("temp_coding.json"):
        os.remove("temp_coding.json")

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
    resp = requests.post(f"{BASE_URL}/admin/quiz/manual", json=quiz_data, headers=headers)
    if resp.status_code == 200:
        print(f"[SUCCESS] Quiz Created: {resp.json()['title']}")
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")

def test_dashboard():
    print("\n--- Testing Check Yourself Dashboard ---")
    # Register/Login a fresh user
    user_email = f"user_{int(time.time())}@dashboard.com"
    requests.post(f"{BASE_URL}/auth/register", json={"email": user_email, "name": "Dashboard User", "password": "password123"})
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": user_email, "password": "password123"})
    user_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    
    resp = requests.get(f"{BASE_URL}/check-yourself", headers=user_headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] Dashboard returned {len(data['assignments'])} assignments and {len(data['quizzes'])} quizzes.")
    else:
        print(f"[FAILED] Status {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    print("=== STARTING ALL TESTS WITH REQUIRED PARAMETERS ===")
    test_pdf_upload_with_params()
    test_coding_upload_with_params()
    test_quiz_manual()
    test_dashboard()
    print("\n=== ALL TESTS COMPLETED ===")
