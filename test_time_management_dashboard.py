import requests
import json

BASE_URL = "http://127.0.0.1:8001/api"

def test_time_management_dashboard():
    print("--- Testing Time Management Dashboard ---")
    
    # 1. Login to get token (using seeded student)
    login_data = {
        "username": "student@cfab.com",
        "password": "student123"
    }
    login_res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Dashboard
    dash_res = requests.get(f"{BASE_URL}/time-management", headers=headers)
    if dash_res.status_code == 200:
        data = dash_res.json()
        print(f"[SUCCESS] Dashboard loaded.")
        print(f"Total Courses: {data['total_courses']}")
        print(f"Active Plans: {len(data['active_courses'])}")
        print(f"Available to Start: {len(data['available_courses'])}")
        
        for ac in data['active_courses']:
            print(f" - Active: {ac['title']} ({ac['progress']:.1f}%)")
            
        for avc in data['available_courses']:
            print(f" - Available: {avc['title']}")
    else:
        print(f"[FAILED] Dashboard Status {dash_res.status_code}: {dash_res.text}")

if __name__ == "__main__":
    test_time_management_dashboard()
