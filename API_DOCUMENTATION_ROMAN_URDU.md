# API Documentation - Check Yourself (Roman Urdu)

Yeh documentation front-end developer ke liye hai taake woh backend APIs ko samajh sakein aur integrate kar sakein. Sabhi endpoints ke liye **Base URL** `http://localhost:8000` hai.

---

## 1. 🔐 Authentication (Login aur Signup)

### Naya User Register Karein
`POST /auth/register`
Is endpoint se naya user register hota hai.

**Request Body (JSON):**
```json
{
  "email": "user@example.com",
  "name": "Full Name",
  "password": "yourpassword",
  "role": "student" 
}
```

### Login Karein
`POST /auth/login`
User login karke access token hasil karta hai. Yeh standard OAuth2 flow use karta hai.

**Request Body (Form-Data):**
- `username`: User ki email
- `password`: User ka password

**Response:**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

## 2. 🏠 Dashboard Data
`GET /check-yourself`
Dashboard ka saara data (Assignments aur Quizzes ki list) ek hi baar mein fetch karne ke liye.

**Headers:**
- `Authorization: Bearer <TOKEN>`

---

## 3. 📝 Assignments (PDF aur Coding)

### Saari Assignments ki List
`GET /assignments`
Sari available assignments ki basic list deta hai.

### Assignment Search Karein
`GET /assignments/search?title=Python`
Title ke zariye assignments search karne ke liye query parameter `title` use karein.

### Assignment ki Detail Hasil Karein
`GET /assignments/{id}`
Kisi specific assignment ki poori detail.
- **PDF Assignment:** Title, description, aur file path milega.
- **Coding Assignment:** Description, starter code, aur visible test cases milenge.

### PDF File Download
`GET /assignments/{id}/file`
Sirf PDF type assignments ke liye, asal PDF file download karne ka endpoint.

---

## 4. 🎓 Quizzes

### Quizzes ki List
`GET /quiz`
Available quizzes aur unke sawalon (questions) ki list deta hai. Note karein ke ismein sahi jawab (correct answers) nahi honge.

### Quiz Submit Karein
`POST /quiz/submit`
User ke jawabat submit karke result/score hasil karne ke liye.

**Request Body (JSON):**
```json
{
  "quiz_id": "645a...",
  "answers": [
    { "question_id": "645b...", "selected": "A" },
    { "question_id": "645c...", "selected": "C" }
  ]
}
```

**Response:**
```json
{
  "score": 8,
  "total": 10
}
```

---

## 5. 💻 Coding Submissions (Practice Code)

### Code Evaluation ke liye Bhejein
`POST /practice-code/submit`
Student apna code yahan submit karta hai. Yeh API foran response deti hai aur code background mein (Celery worker par) run hota hai.

**Request Body (JSON):**
```json
{
  "assignment_id": "645a...",
  "code": "def solve():\n    return True",
  "language": "python"
}
```

**Response:**
```json
{
  "id": "SUBMISSION_ID",
  "status": "pending"
}
```

### Result Poll Karein
`GET /practice-code/{submission_id}`
Submission ID ke zariye check karein ke code run ho gaya ya nahi. Is endpoint ko 2-3 seconds ke gap se baar baar call karna hoga jab tak status `completed` ya `error` na ho jaye.

### Apni Purani Submissions Dekhein
`GET /practice-code/me/list`
User apni pichli sari submissions aur unke results ki list dekh sakta hai.

---

## 🛠️ Admin Endpoints (Sirf Admin Role ke liye)

### PDF Assignment Upload
`POST /assignments/upload` (Form-data)
Admin title, description aur PDF file bhej kar naya assignment bana sakta hai.

### Coding Assignment Banana
`POST /assignments/coding` (JSON)
JSON payload ke zariye coding assignment, starter code aur test cases define karein.

### Quiz PDF Upload
`POST /admin/quiz/upload-pdf` (Form-data)
Agar quiz ki PDF upload karenge toh system automatically sawal aur options extract kar lega.

### Assignment/Quiz Delete
- `DELETE /assignments/{id}`: Kisi bhi assignment ko delete karne ke liye.
- `DELETE /admin/quiz/{id}`: Kisi quiz ko delete karne ke liye.
