# Study aur Time Management API Documentation (Roman Urdu)

Yeh document aapko Study module aur Time Management module ki APIs ke baare mein batayega ke kaunsi API kya kaam karti hai aur unka request structure kya hai.

---

## 1. Study Module (Course aur Lecture Management)

### **Admin: Course Banayein**
- **Endpoint:** `POST /api/study/course/create`
- **Kaam:** Naya course banane ke liye.
- **Request Example:**
  ```json
  {
    "title": "FastAPI Masterclass",
    "description": "Learn FastAPI from scratch"
  }
  ```

### **Admin: Lecture Upload Karein**
- **Endpoint:** `POST /api/study/lecture/upload`
- **Kaam:** Kisi course mein lecture add karne ke liye.
- **Request Example:**
  ```json
  {
    "course_id": "course_id_here",
    "title": "Introduction to API",
    "video_url": "https://youtube.com/link",
    "duration": 45,
    "order_index": 1
  }
  ```

### **Student/Admin: Course ki Lectures Dekhein**
- **Endpoint:** `GET /api/study/lecture/course/{course_id}`
- **Kaam:** Kisi course ki saari lectures list karne ke liye.
- **Response Format:** Lectures ki list milti hai jis mein title, video_url aur duration shamil hote hain.

---

## 2. Time Management Module (Student Dashboard)

### **Time Management Dashboard**
- **Endpoint:** `GET /api/time-management`
- **Kaam:** Student ka entry point. Is mein "active_courses" aur "available_courses" ki list milti hai.

### **Course Shuru Karein (Generate Plan)**
- **Endpoint:** `POST /api/time-management/course/start`
- **Kaam:** Student ki availability ke hisaab se schedule banane ke liye.
- **Request Example:**
  ```json
  {
    "course_id": "course_id_here",
    "daily_minutes": 60,
    "weekly_schedule": {
      "monday": 60,
      "tuesday": 30,
      "wednesday": 90
    }
  }
  ```

### **Study Plan Dekhein**
- **Endpoint:** `GET /api/time-management/study-plan/{course_id}`
- **Kaam:** Student ka locked schedule dekhne ke liye.
- **Response:** Is mein `plan` object milta hai (e.g., "day1": [lecture_objects], "day2": [...]).

### **Lecture Complete Karein**
- **Endpoint:** `POST /api/time-management/lecture/complete`
- **Kaam:** Lecture khatam hone par progress update karne ke liye.
- **Request Example:**
  ```json
  {
    "course_id": "course_id_here",
    "lecture_id": "lecture_id_here"
  }
  ```

### **Progress Check Karein**
- **Endpoint:** `GET /api/time-management/progress/{course_id}`
- **Kaam:** Specific course ki progress status dekhne ke liye.

---

## Aham Points (Frontend Tips)
1. **ID Handling:** Hamesha `id` field use karein, jo ab string format mein hai.
2. **Hydrated Data:** Study Plan API ab lecture ki IDs nahi balki poore objects deti hai, is liye aapko alag se lecture fetch karne ki zaroorat nahi paregi.
3. **Authentication:** Header mein `Authorization: Bearer <token>` bhejna zaroori hai.
