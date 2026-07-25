import hashlib
from typing import List, Optional

from dao import account_dao, student_dao
from models.account import UserAccountInfo
from services import activity_service

ACCOUNT_ROLES = ("Student", "Teacher", "Admin")
ACCOUNT_STATUSES = ("Active", "Locked")


def list_accounts(role: Optional[str] = None, status: Optional[str] = None) -> List[UserAccountInfo]:
    return account_dao.get_all(role=role, status=status)


def next_account_id() -> str:
    return f"AC{account_dao.get_max_account_num() + 1:05d}"


def create_student_account(account_id: str, ma_hs: str, username: str, password: str) -> UserAccountInfo:
    ma_hs = ma_hs.strip()
    username = username.strip()
    if not student_dao.get_by_id(ma_hs):
        raise ValueError("Học sinh không tồn tại.")
    if account_dao.get_by_student(ma_hs):
        raise ValueError("Học sinh này đã có tài khoản.")
    return create_account(account_id, username, password, "Student", ma_hs=ma_hs)


def create_account(
    account_id: str,
    username: str,
    password: str,
    role: str,
    ma_hs: Optional[str] = None,
) -> UserAccountInfo:
    account_id = account_id.strip()
    username = username.strip()
    if not account_id:
        raise ValueError("Mã tài khoản không được để trống.")
    if not username:
        raise ValueError("Tên đăng nhập không được để trống.")
    if len(password) < 6:
        raise ValueError("Mật khẩu phai có it nhat 6 kỳ tu.")
    if role not in ACCOUNT_ROLES:
        raise ValueError("Vai trò tài khoản không hợp lệ.")
    if account_dao.get_by_id(account_id):
        raise ValueError(f"Mã tài khoản '{account_id}' đã tồn tại.")
    if account_dao.get_by_username(username):
        raise ValueError(f"Tên đăng nhập '{username}' đã tồn tại.")
    account = UserAccountInfo(
        account_id=account_id,
        ma_hs=ma_hs,
        username=username,
        password_hash=_hash_password(password),
        role=role,
        status="Active",
    )
    account_dao.insert(account)
    activity_service.log_activity("Tao tài khoản", f"Tao tài khoản {username} ({role})")
    return account


def set_status(account_id: str, status: str) -> bool:
    if status not in ACCOUNT_STATUSES:
        raise ValueError("Trạng thái tài khoản không hợp lệ.")
    ok = account_dao.update_status(account_id, status)
    if ok:
        activity_service.log_activity("Cập nhật tài khoản", f"{account_id}: {status}")
    return ok


def delete_account(account_id: str) -> bool:
    return account_dao.delete(account_id)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
