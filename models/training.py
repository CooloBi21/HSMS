from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseInfo:
    course_id: str
    course_name: str
    credits: int
    grade_level: Optional[str] = None
    prerequisite_id: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CurriculumItemInfo:
    item_id: str
    course_id: str
    grade_level: str
    semester: str
    sequence_no: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class CourseSectionInfo:
    section_id: str
    course_id: str
    class_code: Optional[str] = None
    teacher_id: Optional[str] = None
    capacity: Optional[int] = None
    status: str = "Mo dang ky"


@dataclass
class CourseRegistrationInfo:
    registration_id: str
    section_id: str
    ma_hs: str
    status: str = "Dang ky"
    registered_at: Optional[str] = None


@dataclass
class ClassScheduleInfo:
    schedule_id: str
    section_id: str
    weekday: str
    start_period: int
    end_period: int
    room: str


@dataclass
class AttendanceRecordInfo:
    attendance_id: str
    section_id: str
    ma_hs: str
    attendance_date: str
    status: str
    notes: Optional[str] = None
