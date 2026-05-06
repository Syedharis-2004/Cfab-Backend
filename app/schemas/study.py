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
    id: PydanticObjectId
    total_lectures: int
    total_duration: int
    version: int

    class Config:
        from_attributes = True

class LectureCreate(BaseModel):
    course_id: PydanticObjectId
    title: str
    video_url: str
    duration: int
    order_index: int

class LectureResponse(LectureCreate):
    id: PydanticObjectId
    version_added: int

    class Config:
        from_attributes = True

class StudyPlanStart(BaseModel):
    course_id: PydanticObjectId
    daily_minutes: int
    weekly_schedule: Optional[Dict[str, int]] = None
    start_date: Optional[datetime] = None

class StudyPlanResponse(BaseModel):
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    course_version: int
    daily_minutes: int
    total_duration: int
    total_days: int
    plan: Dict[str, List[PydanticObjectId]]
    start_date: datetime

    class Config:
        from_attributes = True

class LectureComplete(BaseModel):
    course_id: PydanticObjectId
    lecture_id: PydanticObjectId

class ProgressResponse(BaseModel):
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    completed_lectures: List[PydanticObjectId]
    completed_time: int
    last_lecture: Optional[PydanticObjectId]
    progress_percentage: float

    class Config:
        from_attributes = True
