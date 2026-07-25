from dataclasses import dataclass
from typing import Optional


@dataclass
class HocSinhInfo:
    ma_hs: str
    ho_ten: str
    gioi_tinh: Optional[int] = None
    ngay_sinh: Optional[str] = None
    dia_chi: Optional[str] = None
    diem_tb: Optional[float] = None
    ma_lop: Optional[str] = None
    ho_khau: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    learning_status: str = "Đang học"
    policy_type: Optional[str] = None

    @property
    def gioi_tinh_text(self) -> str:
        if self.gioi_tinh == 1:
            return "Nam"
        if self.gioi_tinh == 0:
            return "Nữ"
        return ""
