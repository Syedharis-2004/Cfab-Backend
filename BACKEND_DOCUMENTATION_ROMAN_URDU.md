# Check Yourself - Backend API Documentation (Roman Urdu)

Check Yourself backend ki mukammal documentation mein khush-amdeed. Yeh system PDF assignments, coding practice, AI quizzes, study planning aur Solved Assignment modules ko handle karta hai.

## Main Technologies
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (via Beanie ODM)
- **AI Integration**: Google Gemini API (gemini-2.5-flash)
- **Data Processing**: Pandas, OpenPyXL
- **Background Tasks**: Celery & Redis

---

## 1. Authentication Module (`/api/auth`)
Is module mein user registration aur login handle hota hai.
- `POST /api/register`: Naya account banane ke liye.
- `POST /api/login`: Login karke JWT token hasil karne ke liye.
- `GET /api/me`: Current logged-in user ki details check karne ke liye.

## 2. Assignments Module (`/api/assignments`)
Practice assignments (PDF aur Coding) ki management.
- `GET /api/assignments`: Tamam available assignments ki list.
- `GET /api/assignments/search`: Title ke zariye assignment search karna.
- `GET /api/assignments/{id}`: Kisi specific assignment ki metadata.
- `GET /api/assignments/{id}/file`: PDF file download karne ke liye.

## 3. Quiz Module (`/api/quiz`)
MCQs par mabni testing system.
- `GET /api/quiz`: Tamam available quizzes ki list.
- `GET /api/quiz/{id}`: Quiz ke sawalat aur details.
- `POST /api/quiz/{id}/submit`: Apne answers submit karne ke liye.
- `GET /api/quiz/{id}/results`: Performance aur sahi jawab dekhne ke liye.

## 4. Study & Time Management (`/api/study`, `/api/time-management`)
Personalized study schedule banane ke liye.
- `GET /api/study/courses`: Registered courses ki list.
- `GET /api/study/courses/{id}/lectures`: Kisi course ki lectures hasil karna.
- `POST /api/time-management/course/start`: Daily study hours ke mutabiq schedule banana.
- `GET /api/time-management/dashboard`: Progress aur aanay walay tasks dekhna.

## 5. Solved Assignment Module (`/api/solved-assignment`)
AI ki madad se assignments solve karna aur visualization recommendations.
- `POST /api/solved-assignment/process-python`: PDF sawalat aur dataset upload karein -> Solved assignment hasil karein.
- `POST /api/solved-assignment/process-powerbi`: PDF sawalat aur dataset upload karein -> Power BI config hasil karein.

## 6. Admin Module (`/api/admin-quiz`, `/api/admin-assignments`)
Sirf admins ke liye content management endpoints.
- `POST /api/admin-quiz/upload-pdf`: PDF upload karke auto-MCQ quiz banana.
- `POST /api/assignments/upload`: Nayi PDF assignment upload karna.
- `POST /api/assignments/coding`: Test cases ke sath coding assignment banana.

---

## Error Handling
API standard HTTP codes use karti hai:
- `200 OK`: Request kamiyab rahi.
- `400 Bad Request`: Validation error ya galat input.
- `401 Unauthorized`: Login zaroori hai.
- `403 Forbidden`: Admin access chahiye.
- `404 Not Found`: Resource nahi mila.
- `500 Internal Server Error`: Server mein koi masla aa gaya.

## Running Locally
- **Chalanay ke liye**: `uvicorn app.main:app --reload`
- **Docs**: Interactive documentation `/docs` par available hai.
