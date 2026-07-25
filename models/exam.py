from dataclasses import dataclass
from typing import Optional


@dataclass
class ExamScheduleInfo:
    exam_id: str
    section_id: str
    exam_date: str
    shift: str
    room: str
    exam_type: str


@dataclass
class ExamEligibilityInfo:
    eligibility_id: str
    exam_id: str
    ma_hs: str
    candidate_no: Optional[str] = None
    attendance_eligible: bool = True
    tuition_eligible: bool = True
    status: str = "Du dieu kien"
    notes: Optional[str] = None


@dataclass
class GradeRecordInfo:
    grade_id: str
    section_id: str
    ma_hs: str
    component_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    average10: Optional[float] = None
    gpa4: Optional[float] = None
    letter_grade: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class GradeReviewInfo:
    review_id: str
    grade_id: str
    request_date: str
    reason: str
    status: str = "Moi"
    adjusted_score: Optional[float] = None
    resolution_notes: Optional[str] = None
