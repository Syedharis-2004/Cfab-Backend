# Check Yourself API — Route Documentation

## Overview
- **Base URL**: `http://localhost:8000`
- **Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔐 Authentication
Used for user registration and session management.

- **POST `/auth/register`**
  - **Description**: Create a new account.
  - **Body**: `{ "email": "...", "password": "...", "name": "...", "role": "user" }`
  
- **POST `/auth/login`**
  - **Description**: Obtain a JWT token.
  - **Body**: Form data (username/password).
  - **Returns**: `{ "access_token": "...", "token_type": "bearer" }`

---

## 📚 Assignments (PDF Based)
Endpoints for viewing and submitting standard assignments.

- **GET `/assignments/`**
  - **Description**: Returns a list of all active assignments.
  
- **GET `/assignments/{id}`**
  - **Description**: Returns details for a specific assignment.
  
- **POST `/assignments/{id}/submit`**
  - **Description**: Upload a PDF solution.
  - **Body**: Multipart form data (file).

---

## 📝 Quizzes
Multiple-choice questions with automated scoring.

- **GET `/quiz/`**
  - **Description**: List all available quizzes.
  
- **GET `/quiz/{id}`**
  - **Description**: Get quiz questions (correct answers are hidden).
  
- **POST `/quiz/{id}/submit`**
  - **Description**: Submit answers and get an instant score.
  - **Body**: `{ "answers": [{ "question_id": "...", "choice_index": 0 }, ...] }`

---

## 💻 Coding Practice (Async Sandbox)
Endpoints for submitting code and tracking execution in the Docker sandbox.

- **POST `/submissions/`**
  - **Description**: Submit Python code for evaluation.
  - **Body**: `{ "assignment_id": "...", "code": "..." }`
  - **Returns**: `{ "submission_id": "..." }`
  
- **GET `/submissions/{id}`**
  - **Description**: Poll this endpoint to get the status of the code execution.
  - **Returns Statuses**: `PENDING`, `RUNNING`, `ACCEPTED`, `WRONG_ANSWER`, `RUNTIME_ERROR`.

---

## 🛠️ Admin Management
Requires a user with the "admin" role.

- **POST `/admin/assignments/`**: Create new assignments.
- **POST `/admin/quiz/`**: Create new quizzes.
- **GET `/admin/submissions/`**: View all student submissions.
