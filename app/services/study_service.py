from app.models.study import Course, Lecture, StudyPlan, Progress
from app.schemas.study import CourseCreate, LectureCreate, StudyPlanStart, LectureComplete
from beanie import PydanticObjectId
from fastapi import HTTPException
from math import ceil
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class StudyService:
    @staticmethod
    async def create_course(course_in: CourseCreate) -> Course:
        course = Course(**course_in.model_dump())
        await course.insert()
        return course

    @staticmethod
    async def get_all_courses() -> List[Course]:
        return await Course.find_all().to_list()

    @staticmethod
    async def upload_lecture(lecture_in: LectureCreate) -> Lecture:
        course = await Course.get(lecture_in.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # When new lectures are added, increment version
        course.version += 1
        course.total_lectures += 1
        course.total_duration += lecture_in.duration
        await course.save()
        
        lecture = Lecture(
            **lecture_in.model_dump(),
            version_added=course.version
        )
        await lecture.insert()
        return lecture

    @staticmethod
    async def generate_study_plan(user_id: PydanticObjectId, course_id: PydanticObjectId, plan_in: StudyPlanStart) -> StudyPlan:
        course = await Course.get(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Fetch all lectures for this course version
        lectures = await Lecture.find(
            Lecture.course_id == course_id,
            Lecture.version_added <= course.version
        ).sort(+Lecture.order_index).to_list()
        
        if not lectures:
            raise HTTPException(status_code=400, detail="Course has no lectures")

        # Check if user already has a plan for this course
        existing_plan = await StudyPlan.find_one(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == course_id
        )
        if existing_plan:
            return existing_plan

        # Generation logic
        plan_dict = {}
        day_counter = 1
        current_day_lectures = []
        current_day_minutes = 0
        
        weekly_schedule = plan_in.weekly_schedule or {} 
        weekly_schedule = {k.lower(): v for k, v in weekly_schedule.items()}
        
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        start_date = plan_in.start_date or datetime.utcnow()
        current_date = start_date
        
        lecture_idx = 0
        while lecture_idx < len(lectures):
            day_name = days_of_week[current_date.weekday()]
            available_today = weekly_schedule.get(day_name, plan_in.daily_minutes)
            
            if available_today > 0:
                while lecture_idx < len(lectures):
                    lecture = lectures[lecture_idx]
                    
                    if not current_day_lectures:
                        current_day_lectures.append(lecture.id)
                        current_day_minutes = lecture.duration
                        lecture_idx += 1
                        if current_day_minutes >= available_today:
                            break
                    else:
                        if current_day_minutes + lecture.duration <= available_today:
                            current_day_lectures.append(lecture.id)
                            current_day_minutes += lecture.duration
                            lecture_idx += 1
                        else:
                            break
                
                plan_dict[f"day{day_counter}"] = current_day_lectures
                day_counter += 1
                current_day_lectures = []
                current_day_minutes = 0
                current_date += timedelta(days=1)
            else:
                current_date += timedelta(days=1)
        
        total_study_days = day_counter - 1

        study_plan = StudyPlan(
            user_id=user_id,
            course_id=course_id,
            course_version=course.version,
            daily_minutes=plan_in.daily_minutes,
            weekly_schedule=plan_in.weekly_schedule,
            total_duration=course.total_duration,
            total_days=total_study_days,
            plan=plan_dict,
            start_date=start_date
        )
        await study_plan.insert()
        
        # Initialize progress
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        )
        if not progress:
            progress = Progress(
                user_id=user_id,
                course_id=course_id
            )
            await progress.insert()
            
        return study_plan

    @staticmethod
    async def complete_lecture(user_id: PydanticObjectId, complete_in: LectureComplete) -> Progress:
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == complete_in.course_id
        )
        if not progress:
            raise HTTPException(status_code=404, detail="Progress record not found. Start the course first.")
        
        if complete_in.lecture_id in progress.completed_lectures:
            return progress
        
        lecture = await Lecture.get(complete_in.lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        plan = await StudyPlan.find_one(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == complete_in.course_id
        )
        if not plan:
             raise HTTPException(status_code=404, detail="Study plan not found")

        progress.completed_lectures.append(complete_in.lecture_id)
        progress.completed_time += lecture.duration
        progress.last_lecture = complete_in.lecture_id
        progress.progress_percentage = (progress.completed_time / plan.total_duration) * 100
        
        await progress.save()
        return progress

    @staticmethod
    async def get_progress(user_id: PydanticObjectId, course_id: PydanticObjectId) -> Progress:
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        )
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        return progress

    @staticmethod
    async def get_study_plan(user_id: PydanticObjectId, course_id: PydanticObjectId) -> StudyPlan:
        plan = await StudyPlan.find_one(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == course_id
        )
        if not plan:
            raise HTTPException(status_code=404, detail="Study plan not found")
        return plan
