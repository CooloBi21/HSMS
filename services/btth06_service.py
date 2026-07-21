from typing import List, Optional

from dao import btth06_dao, hoc_sinh_dao
from models.btth06 import BusinessRecordInfo, BusinessRequirementInfo
from services import activity_service

RECORD_STATUSES = ("Moi", "Dang xu ly", "Hoan thanh", "Tam dung")
REQUIREMENT_STATUSES = ("Implemented", "Partial", "Planned")


def list_requirements(
    group_name: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[BusinessRequirementInfo]:
    return btth06_dao.get_requirements(group_name=group_name, status=status, search=search)


def list_groups() -> List[str]:
    return btth06_dao.get_groups()


def requirement_summary() -> dict:
    counts = btth06_dao.count_requirements_by_status()
    total = sum(counts.values())
    return {
        "total": total,
        "implemented": counts.get("Implemented", 0),
        "partial": counts.get("Partial", 0),
        "planned": counts.get("Planned", 0),
        "records": btth06_dao.count_records(),
    }


def list_records(
    requirement_code: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[BusinessRecordInfo]:
    return btth06_dao.get_records(requirement_code=requirement_code, status=status, search=search)


def get_record(record_id: str) -> Optional[BusinessRecordInfo]:
    return btth06_dao.get_record(record_id)


def generate_next_record_id() -> str:
    return f"B{btth06_dao.get_max_record_num() + 1:04d}"


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _validate_record(record: BusinessRecordInfo, is_update: bool = False) -> None:
    if not record.record_id or not record.record_id.strip():
        raise ValueError("Ma ho so nghiep vu khong duoc de trong.")
    if not btth06_dao.get_requirement(record.requirement_code):
        raise ValueError("Yeu cau BTTH06 khong ton tai.")
    if not record.title or not record.title.strip():
        raise ValueError("Tieu de ho so nghiep vu khong duoc de trong.")
    if record.status not in RECORD_STATUSES:
        raise ValueError("Trang thai ho so nghiep vu khong hop le.")
    if record.student_code and not hoc_sinh_dao.get_by_id(record.student_code):
        raise ValueError(f"Hoc sinh '{record.student_code}' khong ton tai.")
    if record.numeric_value is not None and record.numeric_value < 0:
        raise ValueError("Gia tri so khong duoc am.")
    if record.amount is not None and record.amount < 0:
        raise ValueError("So tien khong duoc am.")
    if not is_update and btth06_dao.get_record(record.record_id):
        raise ValueError(f"Ma ho so '{record.record_id}' da ton tai.")


def create_record(record: BusinessRecordInfo) -> BusinessRecordInfo:
    record.record_id = record.record_id.strip()
    record.requirement_code = record.requirement_code.strip()
    record.title = record.title.strip()
    record.student_code = _normalize_optional(record.student_code)
    record.event_date = _normalize_optional(record.event_date)
    record.notes = _normalize_optional(record.notes)
    _validate_record(record, is_update=False)
    btth06_dao.insert_record(record)
    activity_service.log_activity(
        "Them ho so BTTH06",
        f"Them {record.record_id} cho yeu cau {record.requirement_code}: {record.title}",
    )
    return record


def update_record(record: BusinessRecordInfo) -> BusinessRecordInfo:
    record.record_id = record.record_id.strip()
    record.requirement_code = record.requirement_code.strip()
    record.title = record.title.strip()
    record.student_code = _normalize_optional(record.student_code)
    record.event_date = _normalize_optional(record.event_date)
    record.notes = _normalize_optional(record.notes)
    if not btth06_dao.get_record(record.record_id):
        raise ValueError(f"Khong tim thay ho so '{record.record_id}'.")
    _validate_record(record, is_update=True)
    btth06_dao.update_record(record)
    activity_service.log_activity(
        "Cap nhat ho so BTTH06",
        f"Cap nhat {record.record_id} - {record.title}",
    )
    return record


def delete_record(record_id: str) -> bool:
    existing = btth06_dao.get_record(record_id)
    if not existing:
        raise ValueError(f"Khong tim thay ho so '{record_id}'.")
    ok = btth06_dao.delete_record(record_id)
    if ok:
        activity_service.log_activity(
            "Xoa ho so BTTH06",
            f"Xoa {existing.record_id} - {existing.title}",
        )
    return ok
