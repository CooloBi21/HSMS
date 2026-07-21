from dataclasses import dataclass
from typing import Optional


@dataclass
class BusinessRequirementInfo:
    code: str
    group_name: str
    title: str
    description: Optional[str] = None
    status: str = "Planned"
    module_hint: Optional[str] = None


@dataclass
class BusinessRecordInfo:
    record_id: str
    requirement_code: str
    title: str
    status: str
    student_code: Optional[str] = None
    event_date: Optional[str] = None
    numeric_value: Optional[float] = None
    amount: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
