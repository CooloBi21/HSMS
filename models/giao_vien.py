from dataclasses import dataclass
from typing import Optional


@dataclass
class GiaoVienInfo:
    teacher_id: str
    teacher_code: str
    full_name: str
    gender: Optional[int] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None

    @property
    def gioi_tinh_text(self) -> str:
        if self.gender == 1:
            return "Nam"
        if self.gender == 0:
            return "Nữ"
        return ""
