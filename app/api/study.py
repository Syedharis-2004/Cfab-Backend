from fastapi import APIRouter, Depends, status
from typing import List
from beanie import PydanticObjectId
from app.api.auth import get_admin_user, get_current_user
from app.models.user import User
from app.schemas.study import (
    CourseCreate, CourseResponse, 
    LectureCreate, LectureResponse
)
from app.services.study_service import StudyService

router = APIRouter(prefix="/study", tags=["admin-study"])

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

@router.get("/course/all", response_model=List[CourseResponse])
async def get_all_courses_admin(current_admin: User = Depends(get_admin_user)):
    """
    Admin: List all courses for management.
    """
    return await StudyService.get_all_courses()

@router.get("/lecture/course/{course_id}", response_model=List[LectureResponse])
async def get_course_lectures(
    course_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Get all lectures for a specific course.
    Accessible by both students and admins.
    """
    return await StudyService.get_lectures_by_course(course_id)
