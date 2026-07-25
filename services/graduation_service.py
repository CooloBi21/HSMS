from typing import List, Optional

from dao import graduation_dao, student_dao, training_dao
from models.graduation import AlumniEmploymentInfo, DiplomaRecordInfo, DocumentRequestInfo, GraduationCheckInfo
from services import activity_service, dashboard_service, exam_service

DOCUMENT_TYPES = ("Bảng Điểm", "Giấy xác nhận HSSV", "Báo cáo thống kê")
DIPLOMA_STATUSES = ("Đã cấp", "Chờ cấp", "Hủy")
DOCUMENT_STATUSES = ("Mới", "Đề xuất", "Đã in")
EMPLOYMENT_STATUSES = ("Có việc làm", "Chưa có việc làm", "Học tiếp", "Không liên hệ được")


def list_checks(ma_hs: Optional[str] = None) -> List[GraduationCheckInfo]:
    return graduation_dao.get_checks(ma_hs=ma_hs)


def list_diplomas(ma_hs: Optional[str] = None) -> List[DiplomaRecordInfo]:
    return graduation_dao.get_diplomas(ma_hs=ma_hs)


def list_documents(ma_hs: Optional[str] = None) -> List[DocumentRequestInfo]:
    return graduation_dao.get_documents(ma_hs=ma_hs)


def list_alumni(ma_hs: Optional[str] = None) -> List[AlumniEmploymentInfo]:
    return graduation_dao.get_alumni(ma_hs=ma_hs)


def summary() -> dict:
    checks = list_checks()
    alumni = list_alumni()
    return {
        "eligible": len([c for c in checks if c.status == "Đạt"]),
        "diplomas": len(list_diplomas()),
        "documents": len(list_documents()),
        "employed": len([a for a in alumni if a.employment_status == "Có việc làm"]),
    }


def next_check_id() -> str:
    return f"TN{graduation_dao.get_max_num('GRADUATION_CHECK', 'CheckID', 'TN', 2) + 1:05d}"


def next_diploma_id() -> str:
    return f"VB{graduation_dao.get_max_num('DIPLOMA_RECORD', 'DiplomaID', 'VB', 2) + 1:05d}"


def next_document_id() -> str:
    return f"BM{graduation_dao.get_max_num('DOCUMENT_REQUEST', 'RequestID', 'BM', 2) + 1:05d}"


def next_alumni_id() -> str:
    return f"CSV{graduation_dao.get_max_num('ALUMNI_EMPLOYMENT', 'AlumniID', 'CSV', 3) + 1:05d}"


def check_graduation(item: GraduationCheckInfo) -> GraduationCheckInfo:
    _ensure_student(item.ma_hs)
    item.check_date = item.check_date.strip()
    if not item.check_date:
        raise ValueError("Ngày xét tốt nghiệp không được để trống.")
    if item.required_credits <= 0:
        raise ValueError("Số tín chỉ yêu cầu phải lớn hơn 0.")
    if item.earned_credits < 0:
        item.earned_credits = _earned_credits(item.ma_hs)
    passed = (
        item.earned_credits >= item.required_credits
        and item.informatics_cert
        and item.language_cert
        and item.defense_cert
    )
    item.status = "Đạt" if passed else "Chỉa Đạt"
    item.notes = _normalize_optional(item.notes)
    graduation_dao.save_check(item)
    activity_service.log_activity("Xét tốt nghiệp", f"{item.ma_hs}: {item.status}")
    return item


def save_diploma(item: DiplomaRecordInfo) -> DiplomaRecordInfo:
    _ensure_student(item.ma_hs)
    item.registry_no = item.registry_no.strip()
    item.diploma_no = item.diploma_no.strip()
    item.issue_date = item.issue_date.strip()
    item.notes = _normalize_optional(item.notes)
    if not item.registry_no or not item.diploma_no or not item.issue_date:
        raise ValueError("Số gốc, số hiệu bằng và ngày cấp không được để trống.")
    if item.status not in DIPLOMA_STATUSES:
        raise ValueError("Trạng thái văn bằng không hợp lệ.")
    graduation_dao.save_diploma(item)
    activity_service.log_activity("Cấp văn bằng", f"{item.ma_hs} - {item.diploma_no}")
    return item


def save_document_request(item: DocumentRequestInfo) -> DocumentRequestInfo:
    _ensure_student(item.ma_hs)
    item.document_type = item.document_type.strip()
    item.request_date = item.request_date.strip()
    item.output_path = _normalize_optional(item.output_path) or _default_output_path(item)
    item.notes = _normalize_optional(item.notes)
    if item.document_type not in DOCUMENT_TYPES:
        raise ValueError("Loại biểu mẫu không hợp lệ.")
    if item.status not in DOCUMENT_STATUSES:
        raise ValueError("Trạng thái biểu mẫu không hợp lệ.")
    graduation_dao.save_document(item)
    activity_service.log_activity("Xuất biểu mẫu", f"{item.document_type} cho {item.ma_hs}")
    return item


def save_alumni(item: AlumniEmploymentInfo) -> AlumniEmploymentInfo:
    _ensure_student(item.ma_hs)
    item.survey_date = item.survey_date.strip()
    item.company = _normalize_optional(item.company)
    item.position = _normalize_optional(item.position)
    item.notes = _normalize_optional(item.notes)
    if item.employment_status not in EMPLOYMENT_STATUSES:
        raise ValueError("Trạng thái việc làm không hợp lệ.")
    if item.salary is not None and item.salary < 0:
        raise ValueError("Lương không được âm.")
    graduation_dao.save_alumni(item)
    activity_service.log_activity("Khảo sát cựu sinh viên", f"{item.ma_hs}: {item.employment_status}")
    return item


def emis_report() -> dict:
    students = student_dao.get_all()
    total = len(students)
    stopped = len([s for s in students if s.learning_status == "Thôi học"])
    graduated = len([s for s in students if s.learning_status == "Tốt nghiệp"])
    dashboard = dashboard_service.get_dashboard_stats()
    return {
        "total_students": total,
        "dropout_rate": round(stopped / total * 100, 2) if total else 0,
        "graduated_rate": round(graduated / total * 100, 2) if total else 0,
        "avg_score": dashboard.average_score,
        "classes": dashboard.class_count,
    }


def delete_check(check_id: str) -> bool:
    return graduation_dao.delete_check(check_id)


def delete_diploma(diploma_id: str) -> bool:
    return graduation_dao.delete_diploma(diploma_id)


def delete_document(request_id: str) -> bool:
    return graduation_dao.delete_document(request_id)


def delete_alumni(alumni_id: str) -> bool:
    return graduation_dao.delete_alumni(alumni_id)


def _earned_credits(ma_hs: str) -> int:
    total = 0
    for grade in exam_service.list_grades(ma_hs=ma_hs):
        if grade.average10 is not None and grade.average10 >= 4:
            section = training_dao.get_section(grade.section_id)
            course = training_dao.get_course(section.course_id) if section else None
            total += course.credits if course else 0
    return total


def _default_output_path(item: DocumentRequestInfo) -> str:
    name = item.document_type.replace(" ", "_").lower()
    return f"ReportAssets/BTTH06/{name}_{item.ma_hs}_{item.request_id}.txt"


def _ensure_student(ma_hs: str) -> None:
    if not ma_hs or not student_dao.get_by_id(ma_hs):
        raise ValueError("Học sinh không tồn tại.")


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value
