from typing import List, Optional

from dao import student_dao, school_class_dao
from models.student import HocSinhInfo
from services import activity_service

LEARNING_STATUSES = ("Đang học", "Bảo lưu", "Thôi học", "Tốt nghiệp")
POLICY_TYPES = ("Không", "Miễn giảm học phí", "Hộ nghèo", "Vùng sâu vùng xa")


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _validate(hs: HocSinhInfo, is_update: bool = False) -> None:
    if not hs.ma_hs or not hs.ma_hs.strip():
        raise ValueError("Mã học sinh không được để trống.")
    if not hs.ho_ten or not hs.ho_ten.strip():
        raise ValueError("Họ tên không được để trống.")
    if not hs.ma_lop:
        raise ValueError("Phải chọn lớp cho học sinh.")
    if hs.gioi_tinh is None:
        raise ValueError("Phải chọn giới tính.")
    if not hs.ngay_sinh:
        raise ValueError("Ngày sinh không được để trống.")
    if not hs.dia_chi:
        raise ValueError("Địa chỉ không được để trống.")
    if hs.diem_tb is None:
        raise ValueError("Điểm trung bình không được để trống.")
    if hs.diem_tb < 0 or hs.diem_tb > 10:
        raise ValueError("Điểm trung bình phải từ 0 đến 10.")
    if hs.learning_status not in LEARNING_STATUSES:
        raise ValueError("Trạng thái học tập không hợp lệ.")
    if hs.policy_type and hs.policy_type not in POLICY_TYPES:
        raise ValueError("Diện chính sách không hợp lệ.")

    lop = school_class_dao.get_by_id(hs.ma_lop)
    if not lop:
        raise ValueError(f"Lớp '{hs.ma_lop}' không tồn tại.")

    if not is_update and student_dao.get_by_id(hs.ma_hs):
        raise ValueError(f"Mã học sinh '{hs.ma_hs}' đã tồn tại.")


def _prepare_student(hs: HocSinhInfo) -> HocSinhInfo:
    hs.ma_hs = hs.ma_hs.strip()
    hs.ho_ten = hs.ho_ten.strip()
    hs.ngay_sinh = _normalize_optional(hs.ngay_sinh)
    hs.dia_chi = _normalize_optional(hs.dia_chi)
    hs.ho_khau = _normalize_optional(hs.ho_khau)
    hs.parent_name = _normalize_optional(hs.parent_name)
    hs.parent_phone = _normalize_optional(hs.parent_phone)
    legacy_statuses = {
        "Dang hoc": "Đang học",
        "Bịo lưu": "Bảo lưu",
        "Thứi học": "Thôi học",
    }
    hs.learning_status = legacy_statuses.get(hs.learning_status, hs.learning_status) or "Đang học"
    hs.policy_type = _normalize_optional(hs.policy_type) or "Không"
    return hs


def list_students(ma_lop: Optional[str] = None, search: Optional[str] = None) -> List[HocSinhInfo]:
    return student_dao.get_all(ma_lop=ma_lop, search=search)


def get_student(ma_hs: str) -> Optional[HocSinhInfo]:
    return student_dao.get_by_id(ma_hs)


def create_student(hs: HocSinhInfo) -> HocSinhInfo:
    hs = _prepare_student(hs)
    _validate(hs, is_update=False)
    student_dao.insert(hs)
    activity_service.log_activity("Thêm học sinh", f"Thêm học sinh {hs.ho_ten} vao lop {hs.ma_lop}")
    return hs


def update_student(hs: HocSinhInfo) -> HocSinhInfo:
    hs = _prepare_student(hs)
    if not student_dao.get_by_id(hs.ma_hs):
        raise ValueError(f"Không tìm thấy học sinh '{hs.ma_hs}'.")
    _validate(hs, is_update=True)
    student_dao.update(hs)
    activity_service.log_activity("Cập nhật học sinh", f"Cập nhật hồ sơ {hs.ho_ten}")
    return hs


def update_student_profile(hs: HocSinhInfo) -> HocSinhInfo:
    hs = _prepare_student(hs)
    if not student_dao.get_by_id(hs.ma_hs):
        raise ValueError(f"Không tìm thấy học sinh '{hs.ma_hs}'.")
    _validate(hs, is_update=True)
    student_dao.update_profile(hs)
    activity_service.log_activity("Cập nhật lý lịch", f"Cập nhật hồ sơ cá nhân {hs.ho_ten}")
    return hs


def delete_student(ma_hs: str) -> bool:
    existing = student_dao.get_by_id(ma_hs)
    if not existing:
        raise ValueError(f"Không tìm thấy học sinh '{ma_hs}'.")
    ok = student_dao.delete(ma_hs)
    if ok:
        activity_service.log_activity("Xóa học sinh", f"Xóa học sinh {existing.ho_ten} ({ma_hs})")
    return ok


def generate_next_id() -> str:
    max_num = student_dao.get_max_ma_hs()
    return f"S{max_num + 1:03d}"
