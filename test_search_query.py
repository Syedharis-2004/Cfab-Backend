import requests

BASE_URL = "http://127.0.0.1:8000"

def test_required_query_params():
    print("--- Testing Search with Required Query Parameter ---")
    
    # 1. Login to get token
    login_data = {"username": "test@example.com", "password": "password123"}
    auth_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Success: Provide required 'title' query parameter
    params = {"title": "Python"}
    response = requests.get(f"{BASE_URL}/assignments/search", params=params, headers=headers)
    print(f"[SUCCESS] Search with 'title=Python': Status {response.status_code}")
    print(f"Results: {response.json()}")

    # 3. Test Failure: Omit required 'title' query parameter
    response_missing = requests.get(f"{BASE_URL}/assignments/search", headers=headers)
    print(f"\n[EXPECTED FAILURE] Search without 'title': Status {response_missing.status_code}")
    print(f"Error Detail: {response_missing.json()['detail'][0]['msg']}")

if __name__ == "__main__":
    test_required_query_params()
