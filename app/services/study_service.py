from app.models.study import Course, Lecture, StudyPlan, Progress
from app.schemas.study import CourseCreate, LectureCreate, StudyPlanStart, LectureComplete
from beanie import PydanticObjectId
from beanie.operators import In
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
        logger.info(f"Uploading lecture: {lecture_in.title} for course: {lecture_in.course_id}")
        course = await Course.get(lecture_in.course_id)
        if not course:
            logger.error(f"Course not found: {lecture_in.course_id}")
            raise HTTPException(status_code=404, detail="Course not found")
        
        # When new lectures are added, increment version
        course.version += 1
        course.total_lectures += 1
        course.total_duration += lecture_in.duration
        await course.save()
        logger.info(f"Course {course.id} updated to version {course.version}")
        
        lecture = Lecture(
            **lecture_in.model_dump(),
            version_added=course.version
        )
        await lecture.insert()
        logger.info(f"Lecture {lecture.id} inserted with version_added {lecture.version_added}")
        return lecture

    @staticmethod
    async def get_lectures_by_course(course_id: PydanticObjectId) -> List[Lecture]:
        logger.info(f"Fetching lectures for course: {course_id}")
        lectures = await Lecture.find(Lecture.course_id == course_id).sort(+Lecture.order_index).to_list()
        logger.info(f"Found {len(lectures)} lectures")
        return lectures

    @staticmethod
    async def generate_study_plan(user_id: PydanticObjectId, course_id: PydanticObjectId, plan_in: StudyPlanStart) -> StudyPlan:
        logger.info(f"Generating study plan for user {user_id}, course {course_id}")
        course = await Course.get(course_id)
        if not course:
            logger.error(f"Course not found: {course_id}")
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Fetch all lectures for this course version
        lectures = await Lecture.find(
            Lecture.course_id == course_id,
            Lecture.version_added <= course.version
        ).sort(+Lecture.order_index).to_list()
        
        if not lectures:
            logger.warning(f"No lectures found for course {course_id} up to version {course.version}")
            raise HTTPException(status_code=400, detail="Course has no lectures")

        logger.info(f"Found {len(lectures)} lectures for plan generation")

        # Check if user already has a plan for this course
        existing_plan = await StudyPlan.find_one(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == course_id
        )
        if existing_plan:
            logger.info(f"User already has a plan for course {course_id}. Returning hydrated existing plan.")
            return await StudyService._hydrate_plan(existing_plan)

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
            
        return await StudyService._hydrate_plan(study_plan)

    @staticmethod
    async def _hydrate_plan(plan: StudyPlan) -> Dict:
        logger.info(f"Hydrating study plan {plan.id}")
        # Fetch all lecture IDs in the plan
        all_lecture_ids = []
        for day_lectures in plan.plan.values():
            all_lecture_ids.extend(day_lectures)
        
        # Unique IDs
        unique_ids = list(set(all_lecture_ids))
        lectures = await Lecture.find(In(Lecture.id, unique_ids)).to_list()
        lecture_map = {l.id: l for l in lectures}
        
        hydrated_plan = {}
        for day, ids in plan.plan.items():
            hydrated_plan[day] = [lecture_map.get(lid) for lid in ids if lid in lecture_map]
            
        # Convert to dict for response model
        result = plan.model_dump()
        result["plan"] = hydrated_plan
        # Ensure ID is string
        result["id"] = str(plan.id)
        result["user_id"] = str(plan.user_id)
        result["course_id"] = str(plan.course_id)
        
        return result

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
    async def get_study_plan(user_id: PydanticObjectId, course_id: PydanticObjectId) -> Dict:
        logger.info(f"Fetching study plan for user {user_id}, course {course_id}")
        plan = await StudyPlan.find_one(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == course_id
        )
        if not plan:
            logger.warning(f"Study plan not found for user {user_id}, course {course_id}")
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        logger.info(f"Found study plan {plan.id} for course version {plan.course_version}")
        return await StudyService._hydrate_plan(plan)
