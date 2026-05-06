import asyncio
import os
import sys

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from app.core.database import init_db
from app.services.study_service import StudyService
from app.schemas.study import CourseCreate, LectureCreate, StudyPlanStart, LectureComplete
from app.models.user import User
from app.models.study import Course, Lecture, StudyPlan, Progress

async def test_flow():
    print("--- Time Management Module Test ---")
    print("Initializing Database...")
    try:
        await init_db()
    except Exception as e:
        print(f"Failed to initialize DB: {e}")
        return
    
    # 1. Create a dummy user if not exists
    user = await User.find_one(User.email == "test_student@example.com")
    if not user:
        user = User(email="test_student@example.com", name="Test Student", hashed_password="pw", role="user")
        await user.insert()
    print(f"User ready: {user.email}")
    
    # 2. Create Course
    print("\n[Step 1] Creating course...")
    course_in = CourseCreate(title="FastAPI + MongoDB", description="Build scalable backends")
    course = await StudyService.create_course(course_in)
    print(f"Course created: {course.title} (Version: {course.version})")
    
    # 3. Upload Lectures
    print("\n[Step 2] Uploading lectures...")
    lectures_data = [
        ("Setup", 15, 1),
        ("Models", 30, 2),
        ("Routes", 25, 3),
        ("Auth", 45, 4),
    ]
    lecture_ids = []
    for title, duration, order in lectures_data:
        lect = await StudyService.upload_lecture(LectureCreate(
            course_id=course.id,
            title=title,
            video_url=f"http://vid.com/{title}",
            duration=duration,
            order_index=order
        ))
        lecture_ids.append(lect.id)
        print(f"  + {title} ({duration} mins) -> Course Version is now {course.version}")
    
    # Refresh course
    course = await Course.get(course.id)
    print(f"Total Duration: {course.total_duration} mins across {course.total_lectures} lectures.")
    
    # 4. Start Course (Generate Plan with Availability)
    print("\n[Step 3] Starting course (Availability: Mon/Wed/Fri - 60 mins)...")
    schedule = {
        "monday": 60, "tuesday": 0, "wednesday": 60, "thursday": 0, "friday": 60,
        "saturday": 0, "sunday": 0
    }
    plan_in = StudyPlanStart(
        course_id=course.id,
        daily_minutes=30,
        weekly_schedule=schedule
    )
    plan = await StudyService.generate_study_plan(user.id, course.id, plan_in)
    print(f"Plan generated for {plan.total_days} study days.")
    for day, lects in plan.plan.items():
        print(f"  {day}: {len(lects)} lectures")
    
    # 5. Mark lecture as complete
    print("\n[Step 4] Completing 'Setup' lecture...")
    progress = await StudyService.complete_lecture(user.id, LectureComplete(
        course_id=course.id,
        lecture_id=lecture_ids[0]
    ))
    print(f"  Progress: {progress.progress_percentage:.2f}%")
    print(f"  Completed Time: {progress.completed_time} mins")
    
    # 6. Test Versioning (Add more content)
    print("\n[Step 5] Adding 'Deployment' lecture (v5)...")
    await StudyService.upload_lecture(LectureCreate(
        course_id=course.id,
        title="Deployment",
        video_url="http://vid.com/deploy",
        duration=20,
        order_index=5
    ))
    
    # Verify user's plan is still based on original total duration
    plan_after = await StudyPlan.get(plan.id)
    print(f"  User's locked total duration: {plan_after.total_duration} mins")
    
    updated_course = await Course.get(course.id)
    print(f"  Updated Course total duration: {updated_course.total_duration} mins")
    print(f"  Updated Course Version: {updated_course.version}")
    
    # Completing another lecture to see progress calculation against LOCKED duration
    print("\n[Step 6] Completing 'Models' lecture...")
    progress = await StudyService.complete_lecture(user.id, LectureComplete(
        course_id=course.id,
        lecture_id=lecture_ids[1]
    ))
    print(f"  New Progress: {progress.progress_percentage:.2f}% (should be based on 115 total, not 135)")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_flow())
