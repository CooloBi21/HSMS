from dataclasses import dataclass
from typing import Optional


@dataclass
class UserAccountInfo:
    account_id: str
    username: str
    password_hash: str
    role: str
    status: str = "Active"
    ma_hs: Optional[str] = None
    created_at: Optional[str] = None
