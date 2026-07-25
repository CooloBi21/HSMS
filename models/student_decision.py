from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentDecisionInfo:
    decision_id: str
    ma_hs: str
    decision_type: str
    decision_date: str
    title: str
    description: Optional[str] = None
    issuer: Optional[str] = None
    created_at: Optional[str] = None
