import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_full_flow():
    print("--- Starting Full-Flow Integration Test ---")
    
    unique_user = f"user_{uuid.uuid4().hex[:6]}@example.com"
    password = "testpassword"
    
    # 1. Register
    print(f"\n[1] Registering user: {unique_user}")
    reg_data = {
        "email": unique_user,
        "name": "Integration Test User",
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    print("Registration successful!")

    # 2. Login
    print(f"\n[2] Logging in")
    login_data = {"username": unique_user, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful! Token acquired.")

    # 3. Get Modules
    print(f"\n[3] Fetching modules")
    response = requests.get(f"{BASE_URL}/check-yourself", headers=headers)
    assert response.status_code == 200, f"Modules fetch failed: {response.text}"
    print(f"Modules: {response.json()}")

    # 4. Get Assignments
    print(f"\n[4] Fetching assignments")
    response = requests.get(f"{BASE_URL}/assignments", headers=headers)
    assert response.status_code == 200, f"Assignments fetch failed: {response.text}"
    print(f"Assignments count: {len(response.json())}")

    # 5. Search Assignments
    print(f"\n[5] Searching assignments for 'Python'")
    response = requests.get(f"{BASE_URL}/assignments/search", params={"title": "Python"}, headers=headers)
    assert response.status_code == 200, f"Search failed: {response.text}"
    print(f"Search results: {response.json()}")

    # 6. Get Quiz Questions
    print(f"\n[6] Fetching quiz questions")
    response = requests.get(f"{BASE_URL}/quiz", headers=headers)
    assert response.status_code == 200, f"Quiz fetch failed: {response.text}"
    quizzes = response.json()
    print(f"Quiz questions count: {len(quizzes)}")

    # 7. Submit Quiz
    if quizzes:
        print(f"\n[7] Submitting quiz answers")
        submissions = []
        for q in quizzes:
            submissions.append({"quiz_id": q["id"], "selected_answer": "c"}) # 'c' is correct for most seeded ones
        
        response = requests.post(f"{BASE_URL}/quiz/submit", json=submissions, headers=headers)
        assert response.status_code == 200, f"Quiz submission failed: {response.text}"
        print(f"Quiz result: {response.json()}")

    print("\n--- Full-Flow Integration Test Completed Successfully! ---")

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        exit(1)
