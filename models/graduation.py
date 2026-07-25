from dataclasses import dataclass
from typing import Optional


@dataclass
class GraduationCheckInfo:
    check_id: str
    ma_hs: str
    check_date: str
    required_credits: int
    earned_credits: int
    informatics_cert: bool = False
    language_cert: bool = False
    defense_cert: bool = False
    status: str = "Chua dat"
    notes: Optional[str] = None


@dataclass
class DiplomaRecordInfo:
    diploma_id: str
    ma_hs: str
    registry_no: str
    diploma_no: str
    issue_date: str
    status: str = "Da cap"
    graduation_check_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DocumentRequestInfo:
    request_id: str
    ma_hs: str
    document_type: str
    request_date: str
    status: str = "Moi"
    output_path: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class AlumniEmploymentInfo:
    alumni_id: str
    ma_hs: str
    survey_date: str
    employment_status: str
    company: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[float] = None
    notes: Optional[str] = None
