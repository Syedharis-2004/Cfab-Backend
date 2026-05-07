from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from beanie import PydanticObjectId

from app.api.auth import get_current_user
from app.models.user import User
from app.models.study import Course, StudyPlan, Progress
from app.schemas.study import (
    StudyPlanStart, StudyPlanResponse,
    LectureComplete, ProgressResponse,
    TimeManagementDashboard, ActiveCourseItem, AvailableCourseItem
)
from app.services.study_service import StudyService

router = APIRouter(prefix="/time-management", tags=["time-management"])

@router.get("", response_model=TimeManagementDashboard)
async def get_time_management_dashboard(current_user: User = Depends(get_current_user)):
    """
    Unified entry point for the Time Management module.
    Returns active plans (started) and available courses (not started).
    """
    # 1. Get all courses
    courses = await Course.find_all().to_list()
    
    # 2. Get user's progress and plans
    progress_list = await Progress.find(Progress.user_id == current_user.id).to_list()
    plans = await StudyPlan.find(StudyPlan.user_id == current_user.id).to_list()
    
    # Map for easy lookup
    progress_map = {str(p.course_id): p for p in progress_list}
    plan_map = {str(pl.course_id): pl for pl in plans}
    
    active_courses = []
    available_courses = []
    
    for c in courses:
        cid = str(c.id)
        if cid in plan_map:
            p = progress_map.get(cid)
            active_courses.append(ActiveCourseItem(
                id=cid,
                title=c.title,
                progress=p.progress_percentage if p else 0,
                total_lectures=c.total_lectures,
                completed_count=len(p.completed_lectures) if p else 0,
                status="in_progress"
            ))
        else:
            available_courses.append(AvailableCourseItem(
                id=cid,
                title=c.title,
                description=c.description,
                total_lectures=c.total_lectures,
                total_duration=c.total_duration,
                status="not_started"
            ))
            
    return TimeManagementDashboard(
        active_courses=active_courses,
        available_courses=available_courses,
        total_courses=len(courses)
    )

@router.post("/course/start", response_model=StudyPlanResponse)
async def start_course(
    plan_in: StudyPlanStart, 
    current_user: User = Depends(get_current_user)
):
    """
    Start a course by providing daily study time.
    """
    return await StudyService.generate_study_plan(current_user.id, plan_in.course_id, plan_in)

@router.get("/study-plan/{course_id}", response_model=StudyPlanResponse)
async def get_study_plan(course_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    """
    Retrieve the locked study plan for a specific course.
    """
    return await StudyService.get_study_plan(current_user.id, course_id)

@router.post("/lecture/complete", response_model=ProgressResponse)
async def complete_lecture(complete_in: LectureComplete, current_user: User = Depends(get_current_user)):
    """
    Mark a lecture as completed and update progress.
    """
    return await StudyService.complete_lecture(current_user.id, complete_in)

@router.get("/progress/{course_id}", response_model=ProgressResponse)
async def get_progress(course_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    """
    Get user progress for a specific course.
    """
    return await StudyService.get_progress(current_user.id, course_id)
