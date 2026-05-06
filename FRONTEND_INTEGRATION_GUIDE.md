# Check Yourself API — Next.js Frontend Integration Guide

## 🔧 Setup

### Base URL
```js
// lib/api.js
const BASE_URL = "http://127.0.0.1:8000/api";
```

### Axios Instance (Recommended)
```js
// lib/axios.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  withCredentials: false, // Set true ONLY if using cookies for auth
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

> ⚠️ **IMPORTANT**: Do NOT use `withCredentials: true` unless you also need cookies. The backend uses **JWT Bearer tokens**, not cookies.

---

## 🔐 Authentication

### Register
```
POST /api/auth/register
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secret123",
  "role": "student"  // or "admin"
}
```

### Login ⚠️ (Uses form-data, NOT JSON)
```js
const formData = new URLSearchParams();
formData.append("username", email); // field must be "username"
formData.append("password", password);

const res = await axios.post(`${BASE_URL}/auth/login`, formData, {
  headers: { "Content-Type": "application/x-www-form-urlencoded" }
});

localStorage.setItem("access_token", res.data.access_token);
```

---

## 📊 Dashboard

```js
// GET /api/check-yourself
const res = await api.get("/check-yourself");
// res.data = { assignments: [...], quizzes: [...] }
```

---

## 📚 Assignments (PDF)

```js
// List all
await api.get("/assignments");

// Search
await api.get("/assignments/search", { params: { title: "Python" } });

// Get single
await api.get(`/assignments/${id}`);

// Download file (PDF)
const res = await api.get(`/assignments/${id}/file`, { responseType: "blob" });
const url = window.URL.createObjectURL(new Blob([res.data]));
const a = document.createElement("a");
a.href = url;
a.download = "assignment.pdf";
a.click();
```

---

## 📝 Quizzes

```js
// List all quizzes
await api.get("/quiz");

// Get single quiz
await api.get(`/quiz/${quizId}`);

// ⚠️ Submit answers — field is "selected_answer", quiz ID is in URL NOT body
await api.post(`/quiz/${quizId}/submit`, {
  answers: [
    { question_id: "abc123", selected_answer: "B" },
    { question_id: "def456", selected_answer: "A" }
  ]
});
// Response: { score: 3, total: 5 }
```

---

## 💻 Coding Assignments

```js
// Submit code
const res = await api.post("/coding-assignments/submit", {
  assignment_id: assignmentId,
  code: "def solve(a, b): return a + b",
  language: "python"
});
// Returns immediately with status: "pending"
const submissionId = res.data.id;

// Poll for results (every 2s)
const poll = setInterval(async () => {
  const r = await api.get(`/coding-assignments/submissions/${submissionId}`);
  if (r.data.status !== "pending" && r.data.status !== "running") {
    clearInterval(poll);
    // r.data.status = "accepted" | "wrong_answer" | "runtime_error"
    // r.data.score, r.data.passed_cases, r.data.total_cases
  }
}, 2000);

// My submission history
await api.get("/coding-assignments/me/list");
```

---

## 🛠️ Admin — Upload Quiz PDF

```js
// ⚠️ Must use FormData, NOT JSON
const formData = new FormData();
formData.append("title", "Quiz Title");
formData.append("file", pdfFileObject); // from <input type="file">

await api.post("/admin/quiz/upload", formData, {
  headers: { "Content-Type": "multipart/form-data" }
});
```

> **PDF Format** — Must look exactly like this:
> ```
> 1. What is Python?
> A) A snake
> B) A programming language
> C) A database
> D) A framework
> Answer: B
> ```

---

## 🛠️ Admin — Upload PDF Assignment

```js
const formData = new FormData();
formData.append("title", "Assignment Title");
formData.append("description", "Optional description");
formData.append("file", pdfFileObject);

await api.post("/assignments/upload", formData, {
  headers: { "Content-Type": "multipart/form-data" }
});
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| CORS wildcard + credentials | `withCredentials: true` with `*` origin | Use `withCredentials: false` |
| 404 on `/admin/quiz/upload` | Missing `/api` prefix | Use `/api/admin/quiz/upload` |
| 422 on file upload | `title` sent as JSON not form field | Use `FormData` |
| 401 Unauthorized | Missing or expired token | Re-login, check localStorage |
| 500 on quiz PDF upload | PDF format wrong | Follow strict MCQ format above |

---

## 🔗 All Endpoints Quick Reference

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/auth/register` | ❌ | JSON body |
| POST | `/api/auth/login` | ❌ | **form-data**, not JSON |
| GET | `/api/check-yourself` | ✅ | Dashboard |
| GET | `/api/assignments` | ✅ | List all |
| GET | `/api/assignments/search?title=...` | ✅ | Search |
| GET | `/api/assignments/{id}` | ✅ | Detail |
| GET | `/api/assignments/{id}/file` | ✅ | PDF download |
| POST | `/api/assignments/upload` | ✅ Admin | **multipart/form-data** |
| POST | `/api/assignments/coding` | ✅ Admin | JSON body |
| DELETE | `/api/admin/assignments/{id}` | ✅ Admin | |
| GET | `/api/quiz` | ✅ | List |
| GET | `/api/quiz/{id}` | ✅ | Detail |
| POST | `/api/quiz/{id}/submit` | ✅ | `selected_answer` field |
| POST | `/api/admin/quiz` | ✅ Admin | JSON body |
| POST | `/api/admin/quiz/upload` | ✅ Admin | **multipart/form-data** |
| DELETE | `/api/admin/quiz/{id}` | ✅ Admin | |
| POST | `/api/coding-assignments/submit` | ✅ | Code submission |
| GET | `/api/coding-assignments/submissions/{id}` | ✅ | Poll result |
| GET | `/api/coding-assignments/me/list` | ✅ | My submissions |
| GET | `/api/course/all` | ❌ | Public |
| POST | `/api/course/create` | ✅ Admin | |
| POST | `/api/course/start` | ✅ | Start study plan |
| GET | `/api/study-plan/{course_id}` | ✅ | |
| POST | `/api/lecture/upload` | ✅ Admin | |
| POST | `/api/lecture/complete` | ✅ | Mark done |
| GET | `/api/progress/{course_id}` | ✅ | |
| GET | `/docs` | ❌ | **Swagger UI — test all endpoints here** |
