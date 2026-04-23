"""
test_coding_assignments.py — Integration test for the coding assignment feature.

Prerequisites:
  - API is running on http://localhost:8000
  - A user account exists (or will be registered here)
  - seed_coding.py has been run

Run with:
    python test_coding_assignments.py
"""

import time
import requests

BASE = "http://localhost:8000"
EMAIL = "test_coder@example.com"
PASSWORD = "testpassword123"

SEPARATOR = "-" * 55


def header(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


# ---------------------------------------------------------------------------
# 1. Register / Login
# ---------------------------------------------------------------------------
header("1. Auth")

# Register (ignore error if already exists)
r = requests.post(f"{BASE}/auth/register", json={"email": EMAIL, "name": "Test Coder", "password": PASSWORD})
if r.status_code == 200:
    print("  [OK] Registered new user")
elif r.status_code == 400:
    print("  [OK] User already exists, skipping register")
else:
    print(f"  [FAIL] Register: {r.status_code} {r.text}")
    exit(1)

r = requests.post(f"{BASE}/auth/login", data={"username": EMAIL, "password": PASSWORD})
assert r.status_code == 200, f"Login failed: {r.text}"
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("  [OK] Logged in, got JWT")


# ---------------------------------------------------------------------------
# 2. List assignments — should include coding types
# ---------------------------------------------------------------------------
header("2. GET /assignments")
r = requests.get(f"{BASE}/assignments", headers=headers)
assert r.status_code == 200, f"List assignments failed: {r.text}"
assignments = r.json()
print(f"  [OK] Total assignments returned: {len(assignments)}")

coding = [a for a in assignments if a["assignment_type"] == "coding"]
pdf    = [a for a in assignments if a["assignment_type"] == "pdf"]
print(f"       PDF assignments    : {len(pdf)}")
print(f"       Coding assignments : {len(coding)}")

if not coding:
    print("  [WARN] No coding assignments found. Run: python seed_coding.py")
    exit(0)

target = coding[0]
assignment_id = target["id"]
print(f"  [OK] Using: '{target['title']}' (id={assignment_id})")


# ---------------------------------------------------------------------------
# 3. GET /assignments/{id} — coding returns JSON
# ---------------------------------------------------------------------------
header("3. GET /assignments/{id}")
r = requests.get(f"{BASE}/assignments/{assignment_id}", headers=headers)
assert r.status_code == 200, f"Get assignment detail failed: {r.text}"
detail = r.json()
print(f"  [OK] Title       : {detail['title']}")
print(f"  [OK] Type        : {detail['assignment_type']}")
print(f"  [OK] Language    : {detail.get('language')}")
print(f"  [OK] Visible TCs : {len(detail.get('test_cases', []))}")


# ---------------------------------------------------------------------------
# 4. Submit CORRECT code
# ---------------------------------------------------------------------------
header("4. POST /coding-assignments/submit (correct code)")

CORRECT_CODE = "a, b = map(int, input().split())\nprint(a + b)\n"
r = requests.post(
    f"{BASE}/coding-assignments/submit",
    json={"assignment_id": assignment_id, "code": CORRECT_CODE, "language": "python"},
    headers=headers,
)
assert r.status_code == 202, f"Submit failed: {r.status_code} {r.text}"
sub = r.json()
sub_id = sub["id"]
print(f"  [OK] Submission ID : {sub_id}")
print(f"  [OK] Initial status: {sub['status']}")


# ---------------------------------------------------------------------------
# 5. Poll for result
# ---------------------------------------------------------------------------
header("5. Polling submission status")
for attempt in range(15):
    r = requests.get(f"{BASE}/coding-assignments/submissions/{sub_id}", headers=headers)
    assert r.status_code == 200
    status_data = r.json()
    status = status_data["status"]
    print(f"  Attempt {attempt+1:02d}: {status}")
    if status not in ("pending", "running"):
        break
    time.sleep(2)

print(f"\n  Final status : {status_data['status']}")
print(f"  Score        : {status_data['score']}%")
print(f"  Passed       : {status_data['passed_cases']}/{status_data['total_cases']}")
if status_data.get("error_message"):
    print(f"  Error        : {status_data['error_message']}")


# ---------------------------------------------------------------------------
# 6. Submit WRONG code
# ---------------------------------------------------------------------------
header("6. POST /coding-assignments/submit (wrong code)")
WRONG_CODE = "print('wrong answer')\n"
r = requests.post(
    f"{BASE}/coding-assignments/submit",
    json={"assignment_id": assignment_id, "code": WRONG_CODE, "language": "python"},
    headers=headers,
)
assert r.status_code == 202
sub2_id = r.json()["id"]
print(f"  [OK] Submission ID: {sub2_id}")

for attempt in range(15):
    r = requests.get(f"{BASE}/coding-assignments/submissions/{sub2_id}", headers=headers)
    result2 = r.json()
    if result2["status"] not in ("pending", "running"):
        break
    time.sleep(2)

print(f"  Final status : {result2['status']}")
print(f"  Score        : {result2['score']}%")
print(f"  Passed       : {result2['passed_cases']}/{result2['total_cases']}")


# ---------------------------------------------------------------------------
# 7. My submissions
# ---------------------------------------------------------------------------
header("7. GET /coding-assignments/my-submissions")
r = requests.get(f"{BASE}/coding-assignments/my-submissions", headers=headers)
assert r.status_code == 200
my_subs = r.json()
print(f"  [OK] Total submissions for user: {len(my_subs)}")
for s in my_subs[:3]:
    print(f"       {s['id']} | {s['status']:<22} | score={s['score']}%")


print(f"\n{'='*55}")
print("  All tests passed!")
print(f"{'='*55}\n")
