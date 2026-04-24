import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_check_yourself_system():
    print("=== STARTING COMPREHENSIVE TEST ===")
    
    # 1. Admin Login
    print("\n[1] Admin Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@example.com", "password": "admin123"})
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin login successful.")

    # 2. Admin Upload Coding Assignment
    print("\n[2] Admin: Uploading Coding Assignment via JSON...")
    coding_data = {
        "title": "Sum Function Test",
        "description": "Create a function solve(n) that returns the sum of first n numbers.",
        "function_name": "solve",
        "test_cases": [
            {"input": "5", "expected_output": "15", "is_hidden": False},
            {"input": "10", "expected_output": "55", "is_hidden": True}
        ]
    }
    # Create a temporary JSON file to upload
    with open("coding_test.json", "w") as f:
        json.dump(coding_data, f)
    
    with open("coding_test.json", "rb") as f:
        files = {"file": ("coding_test.json", f, "application/json")}
        resp = requests.post(f"{BASE_URL}/admin/coding-assignment/upload", files=files, headers=admin_headers)
    
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
    else:
        print(f"Coding Assignment Uploaded: {resp.json()}")
        assignment_id = resp.json()["assignment_id"]

    # 3. Admin Create Quiz
    print("\n[3] Admin: Creating Quiz Manual...")
    quiz_data = {
        "title": "Python Basics Quiz",
        "questions": [
            {
                "question": "What is 2+2?",
                "option_a": "3",
                "option_b": "4",
                "option_c": "5",
                "option_d": "6",
                "correct_answer": "B"
            },
            {
                "question": "Which keyword is for functions?",
                "option_a": "fun",
                "option_b": "function",
                "option_c": "def",
                "option_d": "define",
                "correct_answer": "C"
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/admin/quiz/manual", json=quiz_data, headers=admin_headers)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
    else:
        print(f"Quiz Created: {resp.json()}")
        quiz_id = str(resp.json()["id"])
        q1_id = resp.json()["questions"][0]["id"]
        q2_id = resp.json()["questions"][1]["id"]

    # 4. User Flow
    print("\n[4] User: Registering and Logging in...")
    user_email = f"user_{int(time.time())}@test.com"
    requests.post(f"{BASE_URL}/auth/register", json={"email": user_email, "name": "User Test", "password": "password123"})
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": user_email, "password": "password123"})
    user_token = resp.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print(f"User login successful: {user_email}")

    # 5. User: Attempt Quiz
    print("\n[5] User: Attempting Quiz (Interactive flow)...")
    # Fetch quiz first (should hide answers)
    resp = requests.get(f"{BASE_URL}/quiz/{quiz_id}", headers=user_headers)
    print(f"Fetched Quiz (answers hidden): {json.dumps(resp.json(), indent=2)}")
    
    # Submit answers
    submit_data = {
        "answers": [
            {"question_id": q1_id, "selected_answer": "B"}, # Correct
            {"question_id": q2_id, "selected_answer": "A"}  # Wrong
        ]
    }
    resp = requests.post(f"{BASE_URL}/quiz/{quiz_id}/submit", json=submit_data, headers=user_headers)
    print(f"Quiz Submission Result: {resp.json()}")

    # 6. User: Submit Coding
    print("\n[6] User: Submitting Code for Evaluation...")
    code_submission = {
        "assignment_id": assignment_id,
        "code": "def solve(n):\n    return sum(range(n + 1))",
        "language": "python"
    }
    resp = requests.post(f"{BASE_URL}/coding-assignments/submit", json=code_submission, headers=user_headers)
    if resp.status_code != 202:
        print(f"FAILED: {resp.text}")
    else:
        submission_id = resp.json()["id"]
        print(f"Code Submitted, Submission ID: {submission_id}. Status: {resp.json()['status']}")
        
        # Poll for results
        print("Polling for results (Celery worker must be running)...")
        for _ in range(10):
            time.sleep(2)
            resp = requests.get(f"{BASE_URL}/coding-assignments/submissions/{submission_id}", headers=user_headers)
            status = resp.json()["status"]
            print(f"Current Status: {status}")
            if status not in ["pending", "running"]:
                print(f"Final Result: {resp.json()}")
                break
    
    # 7. Check Dashboard
    print("\n[7] User: Checking Check Yourself Dashboard...")
    resp = requests.get(f"{BASE_URL}/check-yourself", headers=user_headers)
    print(f"Dashboard Data: {json.dumps(resp.json(), indent=2)}")

    print("\n=== COMPREHENSIVE TEST COMPLETED ===")

if __name__ == "__main__":
    test_check_yourself_system()
