# API Documentation - Check Yourself

This document provides details for the "Check Yourself" backend API endpoints.

## 🔐 Authentication

### Register User
`POST /auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-04-21T..."
}
```

---

### Login
`POST /auth/login`

Authenticate and receive a JWT access token.

**Request Body (OAuth2 Form):**
- `username`: Email address
- `password`: Password

**Response (200 OK):**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

## 🧩 Modules

### Get Modules
`GET /check-yourself`

Returns a list of available modules.

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Response (200 OK):**
```json
["assignment", "quiz"]
```

---

## 📝 Assignments

### List All Assignments
`GET /assignments`

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Basics Practice",
    "created_at": "2026-04-21T..."
  }
]
```

---

### Search Assignments
`GET /assignments/search`

Search assignments by title.

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Query Parameters:**
- `title` (required): The title substring to search for.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Basics Practice",
    "created_at": "2026-04-21T..."
  }
]
```

---

### Get Assignment File
`GET /assignments/{assignment_id}`

Downloads the PDF file for a specific assignment.

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Path Parameters:**
- `assignment_id`: The database ID of the assignment.

**Response (200 OK):**
- Binary PDF file.

---

### Upload Assignment (Admin)
`POST /assignments/upload`

Upload a new assignment PDF.

**Query Parameters:**
- `title`: The title of the assignment.

**Request Body (Multipart Form):**
- `file`: The PDF file.

**Response (200 OK):**
Successfully created assignment object.

---

## 🎓 Quizzes

### Get Quiz Questions
`GET /quiz`

Fetch all available multiple-choice questions.

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "question": "What is the output of print(2**3)?",
    "option_a": "6",
    "option_b": "8",
    "option_c": "9",
    "option_d": "5"
  }
]
```

---

### Submit Quiz
`POST /quiz/submit`

Submit user answers for scoring.

**Headers:**
- `Authorization: Bearer <TOKEN>`

**Request Body:**
```json
[
  {
    "quiz_id": 1,
    "selected_answer": "b"
  }
]
```

**Response (200 OK):**
```json
{
  "score": 1,
  "total": 1
}
```
