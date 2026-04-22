import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_upload_with_query_param():
    print("--- Testing Assignment Upload with Query Parameter ---")
    
    # Create a temporary test file
    test_filename = "test_upload.pdf"
    with open(test_filename, "wb") as f:
        f.write(b"%PDF-1.4 test content")

    # The 'title' is a query parameter in the FastAPI endpoint definition
    # The 'file' is a multipart form field
    params = {"title": "New Practice Assignment"}
    files = {"file": (test_filename, open(test_filename, "rb"), "application/pdf")}

    try:
        response = requests.post(f"{BASE_URL}/assignments/upload", params=params, files=files)
        
        if response.status_code == 200:
            print("[SUCCESS] Upload Successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"[FAILED] Upload Failed with status {response.status_code}")

            print(f"Detail: {response.text}")
            
    finally:
        # Cleanup
        files["file"][1].close()
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    test_upload_with_query_param()
