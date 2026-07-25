from typing import List, Optional

from dao import student_dao, student_decision_dao
from models.student_decision import StudentDecisionInfo
from services import activity_service

DECISION_TYPES = ("Khen thưởng", "Kỷ luật")


def list_decisions(
    ma_hs: Optional[str] = None,
    decision_type: Optional[str] = None,
    search: Optional[str] = None,
) -> List[StudentDecisionInfo]:
    return student_decision_dao.get_all(
        ma_hs=ma_hs,
        decision_type=decision_type,
        search=search,
    )


def get_decision(decision_id: str) -> Optional[StudentDecisionInfo]:
    return student_decision_dao.get_by_id(decision_id)


def generate_next_id() -> str:
    return f"D{student_decision_dao.get_max_decision_num() + 1:04d}"


def decision_summary() -> dict:
    counts = student_decision_dao.count_by_type()
    return {
        "total": sum(counts.values()),
        "reward": counts.get("Khen thưởng", 0),
        "discipline": counts.get("Kỷ luật", 0),
    }


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _validate(decision: StudentDecisionInfo, is_update: bool = False) -> None:
    if not decision.decision_id or not decision.decision_id.strip():
        raise ValueError("Mã quyết định không được để trống.")
    if not student_dao.get_by_id(decision.ma_hs):
        raise ValueError(f"Học sinh '{decision.ma_hs}' không tồn tại.")
    if decision.decision_type not in DECISION_TYPES:
        raise ValueError("Loại quyết định không hợp lệ.")
    if not decision.decision_date:
        raise ValueError("Ngày quyết định không được để trống.")
    if not decision.title or not decision.title.strip():
        raise ValueError("Noi dung quyết định không được để trống.")
    if not is_update and student_decision_dao.get_by_id(decision.decision_id):
        raise ValueError(f"Mã quyết định '{decision.decision_id}' đã tồn tại.")


def _prepare(decision: StudentDecisionInfo) -> StudentDecisionInfo:
    decision.decision_id = decision.decision_id.strip()
    decision.ma_hs = decision.ma_hs.strip()
    decision.decision_date = decision.decision_date.strip()
    decision.title = decision.title.strip()
    decision.description = _normalize_optional(decision.description)
    decision.issuer = _normalize_optional(decision.issuer)
    return decision


def create_decision(decision: StudentDecisionInfo) -> StudentDecisionInfo:
    decision = _prepare(decision)
    _validate(decision, is_update=False)
    student_decision_dao.insert(decision)
    activity_service.log_activity(
        "Thêm quyết định học sinh",
        f"{decision.decision_type} {decision.ma_hs}: {decision.title}",
    )
    return decision


def update_decision(decision: StudentDecisionInfo) -> StudentDecisionInfo:
    decision = _prepare(decision)
    if not student_decision_dao.get_by_id(decision.decision_id):
        raise ValueError(f"Không tìm thấy quyết định '{decision.decision_id}'.")
    _validate(decision, is_update=True)
    student_decision_dao.update(decision)
    activity_service.log_activity(
        "Cập nhật quyết định học sinh",
        f"Cập nhật {decision.decision_id}: {decision.title}",
    )
    return decision


def delete_decision(decision_id: str) -> bool:
    existing = student_decision_dao.get_by_id(decision_id)
    if not existing:
        raise ValueError(f"Không tìm thấy quyết định '{decision_id}'.")
    ok = student_decision_dao.delete(decision_id)
    if ok:
        activity_service.log_activity(
            "Xóa quyết định học sinh",
            f"Xóa {existing.decision_id}: {existing.title}",
        )
    return ok
