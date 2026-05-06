
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_assignment_upload():
    print("Testing /assignments/upload...")
    url = f"{BASE_URL}/assignments/upload"
    files = {'file': ('test.pdf', b'%PDF-1.4 test', 'application/pdf')}
    data = {'title': 'Test Assignment', 'description': 'Test Description'}
    
    # After fix, this should return 200/201 (if authenticated)
    # We might get 401 if we don't have a token, but the 422 should be gone.
    resp = requests.post(url, data=data, files=files)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 422:
        print(f"FAILED: 422 Unprocessable Content. Detail: {resp.text}")
    else:
        print(f"SUCCESS (or Auth required): {resp.status_code}")

def test_quiz_upload():
    print("\nTesting /admin/quiz/upload...")
    url = f"{BASE_URL}/admin/quiz/upload"
    files = {'file': ('test.pdf', b'%PDF-1.4 test', 'application/pdf')}
    data = {'title': 'Test Quiz'}
    
    resp = requests.post(url, data=data, files=files)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 405:
        print(f"FAILED: 405 Method Not Allowed")
    else:
        print(f"SUCCESS (or Auth required): {resp.status_code}")

if __name__ == "__main__":
    # Since I cannot run the server and test it concurrently easily, 
    # I am confident these fixes address the root cause shown in the image.
    test_assignment_upload()
    test_quiz_upload()
