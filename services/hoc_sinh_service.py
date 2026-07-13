from typing import List, Optional

from dao import hoc_sinh_dao, lop_dao
from models.hoc_sinh import HocSinhInfo
from services import activity_service


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
    if hs.diem_tb is not None and (hs.diem_tb < 0 or hs.diem_tb > 10):
        raise ValueError("Điểm trung bình phải từ 0 đến 10.")

    lop = lop_dao.get_by_id(hs.ma_lop)
    if not lop:
        raise ValueError(f"Lớp '{hs.ma_lop}' không tồn tại.")

    if not is_update and hoc_sinh_dao.get_by_id(hs.ma_hs):
        raise ValueError(f"Mã học sinh '{hs.ma_hs}' đã tồn tại.")


def list_students(ma_lop: Optional[str] = None, search: Optional[str] = None) -> List[HocSinhInfo]:
    return hoc_sinh_dao.get_all(ma_lop=ma_lop, search=search)


def get_student(ma_hs: str) -> Optional[HocSinhInfo]:
    return hoc_sinh_dao.get_by_id(ma_hs)


def create_student(hs: HocSinhInfo) -> HocSinhInfo:
    hs.ma_hs = hs.ma_hs.strip()
    hs.ho_ten = hs.ho_ten.strip()
    _validate(hs, is_update=False)
    hoc_sinh_dao.insert(hs)
    activity_service.log_activity("Thêm học sinh", f"Thêm học sinh {hs.ho_ten} vào lớp {hs.ma_lop}")
    return hs


def update_student(hs: HocSinhInfo) -> HocSinhInfo:
    hs.ho_ten = hs.ho_ten.strip()
    if not hoc_sinh_dao.get_by_id(hs.ma_hs):
        raise ValueError(f"Không tìm thấy học sinh '{hs.ma_hs}'.")
    _validate(hs, is_update=True)
    hoc_sinh_dao.update(hs)
    activity_service.log_activity("Cập nhật học sinh", f"Cập nhật hồ sơ {hs.ho_ten}")
    return hs


def delete_student(ma_hs: str) -> bool:
    existing = hoc_sinh_dao.get_by_id(ma_hs)
    if not existing:
        raise ValueError(f"Không tìm thấy học sinh '{ma_hs}'.")
    ok = hoc_sinh_dao.delete(ma_hs)
    if ok:
        activity_service.log_activity("Xóa học sinh", f"Xóa học sinh {existing.ho_ten} ({ma_hs})")
    return ok


def generate_next_id() -> str:
    """Sinh mã học sinh tiếp theo dựa trên mã lớn nhất trong DB (dạng S###)."""
    max_num = hoc_sinh_dao.get_max_ma_hs()
    return f"S{max_num + 1:03d}"
