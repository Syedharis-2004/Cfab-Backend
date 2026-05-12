# Check Yourself - Backend API Documentation (English)

Welcome to the comprehensive documentation for the Check Yourself FastAPI backend. This system provides a platform for PDF assignments, automated coding practice, AI-driven quizzes, personalized study planning, and the Solved Assignment module.

## Core Technologies
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (via Beanie ODM)
- **AI Integration**: Google Gemini API (gemini-2.5-flash)
- **Data Processing**: Pandas, OpenPyXL
- **Background Tasks**: Celery & Redis

---

## 1. Authentication Module (`/api/auth`)
Handles user registration, secure login, and session management.
- `POST /api/register`: Create a new account.
- `POST /api/login`: Authenticate and receive a JWT access token.
- `GET /api/me`: Retrieve current logged-in user details.

## 2. Assignments Module (`/api/assignments`)
Management of practice assignments (PDF and Coding).
- `GET /api/assignments`: List all available assignments.
- `GET /api/assignments/search`: Search assignments by title.
- `GET /api/assignments/{id}`: Get detailed assignment metadata.
- `GET /api/assignments/{id}/file`: Download the assignment PDF file.

## 3. Quiz Module (`/api/quiz`)
Interactive MCQ-based testing.
- `GET /api/quiz`: List all available quizzes.
- `GET /api/quiz/{id}`: Get quiz questions and details.
- `POST /api/quiz/{id}/submit`: Submit answers for evaluation.
- `GET /api/quiz/{id}/results`: View performance and correct answers.

## 4. Study & Time Management (`/api/study`, `/api/time-management`)
Personalized learning schedules.
- `GET /api/study/courses`: List registered courses.
- `GET /api/study/courses/{id}/lectures`: Get all lectures for a specific course.
- `POST /api/time-management/course/start`: Initialize a personalized schedule based on daily study hours.
- `GET /api/time-management/dashboard`: View current progress and upcoming tasks.

## 5. Solved Assignment Module (`/api/solved-assignment`)
AI-powered data analysis and visualization recommendations.
- `POST /api/solved-assignment/process-python`: Upload PDF questions + Dataset -> Receive solved assignment.
- `POST /api/solved-assignment/process-powerbi`: Upload PDF questions + Dataset -> Receive Power BI visualization config.

## 6. Admin Module (`/api/admin-quiz`, `/api/admin-assignments`)
Restricted endpoints for content management.
- `POST /api/admin-quiz/upload-pdf`: Upload a PDF to automatically generate an MCQ quiz.
- `POST /api/assignments/upload`: Upload a new PDF assignment.
- `POST /api/assignments/coding`: Create a new coding assignment with test cases.

---

## Error Handling
The API uses standard HTTP status codes:
- `200 OK`: Request succeeded.
- `400 Bad Request`: Validation error or invalid input.
- `401 Unauthorized`: Authentication required.
- `403 Forbidden`: Admin privileges required.
- `404 Not Found`: Resource does not exist.
- `500 Internal Server Error`: Unexpected server-side error.

## Development & Deployment
- **Local Run**: `uvicorn app.main:app --reload`
- **Docs**: Interactive Swagger documentation available at `/docs`.
