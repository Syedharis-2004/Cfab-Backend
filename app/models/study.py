from beanie import Document, PydanticObjectId, Indexed
from typing import List, Optional, Dict
from datetime import datetime

class Course(Document):
    title: str
    description: str
    total_lectures: int = 0
    total_duration: int = 0  # in minutes
    version: int = 1

    class Settings:
        name = "courses"

class Lecture(Document):
    course_id: PydanticObjectId
    title: str
    video_url: str
    duration: int  # in minutes
    order_index: int
    version_added: int

    class Settings:
        name = "lectures"

class StudyPlan(Document):
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    course_version: int
    daily_minutes: int
    weekly_schedule: Optional[Dict[str, int]] = None  # e.g., {"monday": 60, "tuesday": 30}
    total_duration: int
    total_days: int
    plan: Dict[str, List[PydanticObjectId]]  # "day1": [lecture_id1, lecture_id2]
    start_date: datetime = datetime.utcnow()

    class Settings:
        name = "study_plans"

class Progress(Document):
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    completed_lectures: List[PydanticObjectId] = []
    completed_time: int = 0
    last_lecture: Optional[PydanticObjectId] = None
    progress_percentage: float = 0.0

    class Settings:
        name = "progress"
