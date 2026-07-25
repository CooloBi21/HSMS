from dataclasses import dataclass
from typing import Optional


@dataclass
class AdmissionApplicationInfo:
    application_id: str
    full_name: str
    gender: Optional[int] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    admission_score: Optional[float] = None
    desired_class: Optional[str] = None
    desired_major: Optional[str] = None
    status: str = "Moi"
    student_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def gender_text(self) -> str:
        if self.gender == 1:
            return "Nam"
        if self.gender == 0:
            return "Nu"
        return ""
