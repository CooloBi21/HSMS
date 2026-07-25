from typing import List, Optional

from dao import student_dao, student_affairs_dao
from models.student_affairs import (
    ConductScoreInfo,
    DormAssignmentInfo,
    ExtracurricularActivityInfo,
    HealthRecordInfo,
)
from services import activity_service

DORM_STATUSES = ("Đang ở", "Đã rời", "Tạm vắng")
ACTIVITY_STATUSES = ("Tham gia", "Hoàn thành", "Hủy")
HEALTH_STATUSES = ("Bình thường", "Cần theo dõi", "Điều trị")


def list_conduct_scores(ma_hs: Optional[str] = None) -> List[ConductScoreInfo]:
    return student_affairs_dao.get_conduct_scores(ma_hs=ma_hs)


def list_dorm_assignments(ma_hs: Optional[str] = None, status: Optional[str] = None) -> List[DormAssignmentInfo]:
    return student_affairs_dao.get_dorm_assignments(ma_hs=ma_hs, status=status)


def list_activities(ma_hs: Optional[str] = None) -> List[ExtracurricularActivityInfo]:
    return student_affairs_dao.get_activities(ma_hs=ma_hs)


def list_health_records(ma_hs: Optional[str] = None) -> List[HealthRecordInfo]:
    return student_affairs_dao.get_health_records(ma_hs=ma_hs)


def summary() -> dict:
    dorms = list_dorm_assignments(status="Đang ở")
    health = list_health_records()
    return {
        "conduct": len(list_conduct_scores()),
        "dorm": len(dorms),
        "activities": len(list_activities()),
        "health_alerts": len([h for h in health if h.health_status != "Bình thường"]),
    }


def next_conduct_id() -> str:
    return f"RL{student_affairs_dao.get_max_num('CONDUCT_SCORE', 'ConductID', 'RL', 2) + 1:05d}"


def next_dorm_id() -> str:
    return f"KTX{student_affairs_dao.get_max_num('DORM_ASSIGNMENT', 'DormID', 'KTX', 3) + 1:05d}"


def next_activity_id() -> str:
    return f"NK{student_affairs_dao.get_max_num('EXTRACURRICULAR_ACTIVITY', 'ActivityID', 'NK', 2) + 1:05d}"


def next_health_id() -> str:
    return f"YT{student_affairs_dao.get_max_num('HEALTH_RECORD', 'HealthID', 'YT', 2) + 1:05d}"


def save_conduct_score(item: ConductScoreInfo) -> ConductScoreInfo:
    _ensure_student(item.ma_hs)
    item.term = item.term.strip()
    if not item.term:
        raise ValueError("Học kỳ/nam học không được để trống.")
    scores = [item.awareness_score or 0, item.discipline_score or 0, item.activity_score or 0]
    if any(score < 0 or score > 100 for score in scores):
        raise ValueError("Điểm thành phần phải từ 0 đến 100.")
    item.total_score = round(sum(scores) / 3, 2)
    item.rating = _conduct_rating(item.total_score)
    item.notes = _normalize_optional(item.notes)
    student_affairs_dao.save_conduct_score(item)
    activity_service.log_activity("Cham Điểm rèn luyện", f"{item.ma_hs} - {item.term}: {item.total_score:g}")
    return item


def save_dorm_assignment(item: DormAssignmentInfo) -> DormAssignmentInfo:
    _ensure_student(item.ma_hs)
    item.building = item.building.strip()
    item.room = item.room.strip()
    item.start_date = item.start_date.strip()
    item.bed = _normalize_optional(item.bed)
    item.end_date = _normalize_optional(item.end_date)
    item.notes = _normalize_optional(item.notes)
    if not item.building or not item.room or not item.start_date:
        raise ValueError("Tòa nhà, phòng và ngày bắt đầu không được để trống.")
    if item.status not in DORM_STATUSES:
        raise ValueError("Trạng thái KTX không hợp lệ.")
    if item.electric_water_fee < 0:
        raise ValueError("Tiền điện nước không được âm.")
    active = [d for d in list_dorm_assignments(ma_hs=item.ma_hs, status="Đang ở") if d.dorm_id != item.dorm_id]
    if item.status == "Đang ở" and active:
        raise ValueError("Học sinh đã có phòng KTX Đang o.")
    student_affairs_dao.save_dorm_assignment(item)
    activity_service.log_activity("Cập nhật KTX", f"{item.ma_hs} - {item.building}/{item.room}")
    return item


def save_activity(item: ExtracurricularActivityInfo) -> ExtracurricularActivityInfo:
    _ensure_student(item.ma_hs)
    item.activity_name = item.activity_name.strip()
    item.activity_type = item.activity_type.strip()
    item.join_date = item.join_date.strip()
    item.role = _normalize_optional(item.role)
    item.notes = _normalize_optional(item.notes)
    if not item.activity_name or not item.activity_type or not item.join_date:
        raise ValueError("Tên hoạt động, loại và ngày tham gia không được để trống.")
    if item.hours < 0:
        raise ValueError("Số giờ tham gia không được âm.")
    if item.status not in ACTIVITY_STATUSES:
        raise ValueError("Trạng thái hoat dong không hợp lệ.")
    student_affairs_dao.save_activity(item)
    activity_service.log_activity("Hoạt động ngoại khóa", f"{item.ma_hs} tham gia {item.activity_name}")
    return item


def save_health_record(item: HealthRecordInfo) -> HealthRecordInfo:
    _ensure_student(item.ma_hs)
    item.checkup_date = item.checkup_date.strip()
    item.insurance_no = _normalize_optional(item.insurance_no)
    item.insurance_expiry = _normalize_optional(item.insurance_expiry)
    item.notes = _normalize_optional(item.notes)
    if not item.checkup_date:
        raise ValueError("Ngày khám sức khỏe không được để trống.")
    if item.health_status not in HEALTH_STATUSES:
        raise ValueError("Trạng thái sức khỏe không hợp lệ.")
    if item.height_cm is not None and item.height_cm <= 0:
        raise ValueError("Chiều cao phải lớn hơn 0.")
    if item.weight_kg is not None and item.weight_kg <= 0:
        raise ValueError("Cân nặng phải lớn hơn 0.")
    student_affairs_dao.save_health_record(item)
    activity_service.log_activity("Y tế học đường", f"Cập nhật sức khỏe {item.ma_hs}")
    return item


def delete_conduct_score(conduct_id: str) -> bool:
    return student_affairs_dao.delete_conduct_score(conduct_id)


def delete_dorm_assignment(dorm_id: str) -> bool:
    return student_affairs_dao.delete_dorm_assignment(dorm_id)


def delete_activity(activity_id: str) -> bool:
    return student_affairs_dao.delete_activity(activity_id)


def delete_health_record(health_id: str) -> bool:
    return student_affairs_dao.delete_health_record(health_id)


def _ensure_student(ma_hs: str) -> None:
    if not ma_hs or not student_dao.get_by_id(ma_hs):
        raise ValueError("Học sinh không tồn tại.")


def _conduct_rating(score: float) -> str:
    if score >= 90:
        return "Xuất sốc"
    if score >= 80:
        return "Tot"
    if score >= 65:
        return "Khá"
    if score >= 50:
        return "Đạt"
    return "Cần rèn luyện"


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value
