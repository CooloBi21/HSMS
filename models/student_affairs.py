from dataclasses import dataclass
from typing import Optional


@dataclass
class ConductScoreInfo:
    conduct_id: str
    ma_hs: str
    term: str
    awareness_score: Optional[float] = None
    discipline_score: Optional[float] = None
    activity_score: Optional[float] = None
    total_score: float = 0
    rating: str = "Dat"
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class DormAssignmentInfo:
    dorm_id: str
    ma_hs: str
    building: str
    room: str
    bed: Optional[str] = None
    start_date: str = ""
    end_date: Optional[str] = None
    electric_water_fee: float = 0
    status: str = "Dang o"
    notes: Optional[str] = None


@dataclass
class ExtracurricularActivityInfo:
    activity_id: str
    ma_hs: str
    activity_name: str
    activity_type: str
    join_date: str
    role: Optional[str] = None
    hours: float = 0
    status: str = "Tham gia"
    notes: Optional[str] = None


@dataclass
class HealthRecordInfo:
    health_id: str
    ma_hs: str
    checkup_date: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    health_status: str = "Binh thuong"
    insurance_no: Optional[str] = None
    insurance_expiry: Optional[str] = None
    notes: Optional[str] = None
