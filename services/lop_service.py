from typing import List, Optional

from dao import hoc_sinh_dao, lop_dao
from models.lop import LopInfo
from services import activity_service


def _validate(lop: LopInfo, is_update: bool = False) -> None:
    if not lop.ma_lop or not lop.ma_lop.strip():
        raise ValueError("Mã lớp không được để trống.")
    if not lop.ten_lop or not lop.ten_lop.strip():
        raise ValueError("Tên lớp không được để trống.")
    if not lop.khoi:
        raise ValueError("Khoi khong duoc de trong.")
    if not is_update and lop_dao.get_by_id(lop.ma_lop):
        raise ValueError(f"Mã lớp '{lop.ma_lop}' đã tồn tại.")


def list_classes() -> List[LopInfo]:
    return lop_dao.get_all()


def get_class(ma_lop: str) -> Optional[LopInfo]:
    return lop_dao.get_by_id(ma_lop)


def create_class(lop: LopInfo) -> LopInfo:
    lop.ma_lop = lop.ma_lop.strip()
    lop.ten_lop = lop.ten_lop.strip()
    _validate(lop, is_update=False)
    lop_dao.insert(lop)
    activity_service.log_activity("Thêm lớp", f"Thêm lớp {lop.ten_lop} ({lop.ma_lop})")
    return lop


def update_class(lop: LopInfo) -> LopInfo:
    lop.ten_lop = lop.ten_lop.strip()
    if not lop_dao.get_by_id(lop.ma_lop):
        raise ValueError(f"Không tìm thấy lớp '{lop.ma_lop}'.")
    _validate(lop, is_update=True)
    lop_dao.update(lop)
    activity_service.log_activity("Cập nhật lớp", f"Cập nhật lớp {lop.ten_lop}")
    return lop


def delete_class(ma_lop: str) -> bool:
    existing = lop_dao.get_by_id(ma_lop)
    if not existing:
        raise ValueError(f"Không tìm thấy lớp '{ma_lop}'.")
    count = hoc_sinh_dao.count_by_class(ma_lop)
    if count > 0:
        raise ValueError(f"Không thể xóa lớp đang có {count} học sinh.")
    ok = lop_dao.delete(ma_lop)
    if ok:
        activity_service.log_activity("Xóa lớp", f"Xóa lớp {existing.ten_lop}")
    return ok


def student_count(ma_lop: str) -> int:
    return hoc_sinh_dao.count_by_class(ma_lop)


def generate_next_id() -> str:
    max_num = lop_dao.get_max_ma_lop_num()
    return f"C{max_num + 1:02d}"
