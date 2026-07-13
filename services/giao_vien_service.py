import re
from typing import List, Optional

from dao import giao_vien_dao
from models.giao_vien import GiaoVienInfo
from services import activity_service

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\d{9,11}$")


def _validate(gv: GiaoVienInfo, is_update: bool = False) -> None:
    if not gv.teacher_id or not gv.teacher_id.strip():
        raise ValueError("Mã giáo viên không được để trống.")
    if not gv.teacher_code or not gv.teacher_code.strip():
        raise ValueError("Mã số giáo viên không được để trống.")
    if not gv.full_name or not gv.full_name.strip():
        raise ValueError("Họ tên giáo viên không được để trống.")
    if gv.gender is None:
        raise ValueError("Phải chọn giới tính.")
    if not gv.dob:
        raise ValueError("Ngày sinh không được để trống.")
    if not gv.phone:
        raise ValueError("Số điện thoại không được để trống.")
    if not gv.email:
        raise ValueError("Email không được để trống.")
    if not gv.address:
        raise ValueError("Địa chỉ không được để trống.")
    if not gv.subject:
        raise ValueError("Môn dạy không được để trống.")
    if gv.email and not _EMAIL_RE.match(gv.email):
        raise ValueError("Email không hợp lệ.")
    if gv.phone and not _PHONE_RE.match(gv.phone):
        raise ValueError("Số điện thoại phải gồm 9–11 chữ số.")
    if gv.status and gv.status not in ("Active", "Inactive"):
        raise ValueError("Trạng thái phải là Active hoặc Inactive.")

    if not is_update and giao_vien_dao.get_by_id(gv.teacher_id):
        raise ValueError(f"Mã giáo viên '{gv.teacher_id}' đã tồn tại.")


def list_teachers(search: Optional[str] = None, status: Optional[str] = None) -> List[GiaoVienInfo]:
    return giao_vien_dao.get_all(search=search, status=status)


def get_teacher(teacher_id: str) -> Optional[GiaoVienInfo]:
    return giao_vien_dao.get_by_id(teacher_id)


def get_teacher_by_code(teacher_code: str) -> Optional[GiaoVienInfo]:
    return giao_vien_dao.get_by_code(teacher_code)


def create_teacher(gv: GiaoVienInfo) -> GiaoVienInfo:
    gv.teacher_id = gv.teacher_id.strip()
    gv.teacher_code = gv.teacher_code.strip()
    gv.full_name = gv.full_name.strip()
    if not gv.status:
        gv.status = "Active"
    _validate(gv, is_update=False)
    giao_vien_dao.insert(gv)
    activity_service.log_activity("Thêm giáo viên", f"Thêm GV {gv.full_name} — {gv.subject or 'Chưa có môn'}")
    return gv


def update_teacher(gv: GiaoVienInfo) -> GiaoVienInfo:
    gv.teacher_code = gv.teacher_code.strip()
    gv.full_name = gv.full_name.strip()
    if not giao_vien_dao.get_by_id(gv.teacher_id):
        raise ValueError(f"Không tìm thấy giáo viên '{gv.teacher_id}'.")
    _validate(gv, is_update=True)
    giao_vien_dao.update(gv)
    activity_service.log_activity("Cập nhật giáo viên", f"Cập nhật hồ sơ {gv.full_name}")
    return gv


def delete_teacher(teacher_id: str) -> bool:
    existing = giao_vien_dao.get_by_id(teacher_id)
    if not existing:
        raise ValueError(f"Không tìm thấy giáo viên '{teacher_id}'.")
    ok = giao_vien_dao.delete(teacher_id)
    if ok:
        activity_service.log_activity("Xóa giáo viên", f"Xóa giáo viên {existing.full_name}")
    return ok


def generate_next_code() -> str:
    """Sinh mã số giáo viên tiếp theo dựa trên mã lớn nhất trong DB (dạng GV###)."""
    max_num = giao_vien_dao.get_max_teacher_code_num()
    return f"GV{max_num + 1:03d}"
