from pydantic import BaseModel
from beanie import PydanticObjectId
from typing import List, Optional, Dict
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: str

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: str
    total_lectures: int
    total_duration: int
    version: int

    class Config:
        from_attributes = True
        populate_by_name = True

class LectureCreate(BaseModel):
    course_id: PydanticObjectId
    title: str
    video_url: str
    duration: int
    order_index: int

class LectureResponse(BaseModel):
    id: str
    course_id: str
    title: str
    video_url: str
    duration: int
    order_index: int
    version_added: int

    class Config:
        from_attributes = True
        populate_by_name = True

class StudyPlanStart(BaseModel):
    course_id: PydanticObjectId
    daily_minutes: int
    weekly_schedule: Optional[Dict[str, int]] = None
    start_date: Optional[datetime] = None

class StudyPlanResponse(BaseModel):
    user_id: str
    course_id: str
    course_version: int
    daily_minutes: int
    total_duration: int
    total_days: int
    plan: Dict[str, List[LectureResponse]]
    start_date: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class LectureComplete(BaseModel):
    course_id: PydanticObjectId
    lecture_id: PydanticObjectId

class ProgressResponse(BaseModel):
    user_id: str
    course_id: str
    completed_lectures: List[str]
    completed_time: int
    last_lecture: Optional[str]
    progress_percentage: float

    class Config:
        from_attributes = True
        populate_by_name = True

# --- Dashboard Schemas ---

class ActiveCourseItem(BaseModel):
    id: str
    title: str
    progress: float
    total_lectures: int
    completed_count: int
    status: str

class AvailableCourseItem(BaseModel):
    id: str
    title: str
    description: str
    total_lectures: int
    total_duration: int
    status: str

class TimeManagementDashboard(BaseModel):
    active_courses: List[ActiveCourseItem]
    available_courses: List[AvailableCourseItem]
    total_courses: int
