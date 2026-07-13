from dataclasses import dataclass
from typing import Optional


@dataclass
class LopInfo:
    ma_lop: str
    ten_lop: str
    khoi: Optional[str] = None
