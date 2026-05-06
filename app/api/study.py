from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId

from app.api.auth import get_current_user, get_admin_user
from app.models.user import User
from app.schemas.study import (
    CourseCreate, CourseResponse, 
    LectureCreate, LectureResponse,
    StudyPlanStart, StudyPlanResponse,
    LectureComplete, ProgressResponse
)
from app.services.study_service import StudyService

router = APIRouter(tags=["study"])

# --- Admin Routes ---

@router.post("/course/create", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course_in: CourseCreate, current_admin: User = Depends(get_admin_user)):
    """
    Admin: Create a new course.
    """
    return await StudyService.create_course(course_in)

@router.post("/lecture/upload", response_model=LectureResponse)
async def upload_lecture(lecture_in: LectureCreate, current_admin: User = Depends(get_admin_user)):
    """
    Admin: Upload a lecture to a course. 
    This will increment the course version.
    """
    return await StudyService.upload_lecture(lecture_in)

# --- User Routes ---

@router.get("/course/all", response_model=List[CourseResponse])
async def get_all_courses():
    """
    List all available courses.
    """
    return await StudyService.get_all_courses()

@router.post("/course/start", response_model=StudyPlanResponse)
async def start_course(
    plan_in: StudyPlanStart, 
    current_user: User = Depends(get_current_user)
):
    """
    Start a course by providing daily study time and optional weekly schedule.
    This generates and locks a personalized study plan.
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
