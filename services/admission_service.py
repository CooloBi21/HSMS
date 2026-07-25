from typing import List, Optional

from dao import admission_dao, school_class_dao
from models.admission import AdmissionApplicationInfo
from models.student import HocSinhInfo
from services import activity_service, student_service

APPLICATION_STATUSES = ("Mới", "Đạt", "Không Đạt", "Đã nhập học")
DEFAULT_PASS_SCORE = 5.0


def list_applications(
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[AdmissionApplicationInfo]:
    return admission_dao.get_all(status=status, search=search)


def get_application(application_id: str) -> Optional[AdmissionApplicationInfo]:
    return admission_dao.get_by_id(application_id)


def generate_next_id() -> str:
    return f"A{admission_dao.get_max_application_num() + 1:03d}"


def admission_summary() -> dict:
    counts = admission_dao.count_by_status()
    total = sum(counts.values())
    return {
        "total": total,
        "new": counts.get("Mới", 0),
        "passed": counts.get("Đạt", 0),
        "failed": counts.get("Không Đạt", 0),
        "enrolled": counts.get("Đã nhập học", 0),
    }


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _validate_application(app: AdmissionApplicationInfo, is_update: bool = False) -> None:
    if not app.application_id or not app.application_id.strip():
        raise ValueError("Mã hồ sơ tuyển sinh không được để trống.")
    if not app.full_name or not app.full_name.strip():
        raise ValueError("Họ tên thí sinh không được để trống.")
    if app.gender is None:
        raise ValueError("Phải chọn giới tính.")
    if not app.dob:
        raise ValueError("Ngày sinh không được để trống.")
    if not app.address:
        raise ValueError("Địa chỉ không được để trống.")
    if app.admission_score is None:
        raise ValueError("Điểm xét tuyển không được để trống.")
    if app.admission_score < 0 or app.admission_score > 10:
        raise ValueError("Điểm xét tuyển phải từ 0 đến 10.")
    if app.desired_class and not school_class_dao.get_by_id(app.desired_class):
        raise ValueError(f"Lớp '{app.desired_class}' không tồn tại.")
    if app.status not in APPLICATION_STATUSES:
        raise ValueError("Trạng thái hồ sơ tuyển sinh không hợp lệ.")
    if not is_update and admission_dao.get_by_id(app.application_id):
        raise ValueError(f"Mã hồ sơ '{app.application_id}' đã tồn tại.")


def _clean_application(app: AdmissionApplicationInfo) -> AdmissionApplicationInfo:
    app.application_id = app.application_id.strip()
    app.full_name = app.full_name.strip()
    app.dob = _normalize_optional(app.dob)
    app.address = _normalize_optional(app.address)
    app.phone = _normalize_optional(app.phone)
    app.parent_name = _normalize_optional(app.parent_name)
    app.parent_phone = _normalize_optional(app.parent_phone)
    app.desired_class = _normalize_optional(app.desired_class)
    app.desired_major = _normalize_optional(app.desired_major)
    app.student_code = _normalize_optional(app.student_code)
    app.notes = _normalize_optional(app.notes)
    return app


def create_application(app: AdmissionApplicationInfo) -> AdmissionApplicationInfo:
    app = _clean_application(app)
    app.status = app.status or "Mới"
    _validate_application(app, is_update=False)
    admission_dao.insert(app)
    activity_service.log_activity(
        "Tiếp nhận hồ sơ",
        f"Tiếp nhận hồ sơ tuyển sinh {app.application_id} - {app.full_name}",
    )
    return app


def update_application(app: AdmissionApplicationInfo) -> AdmissionApplicationInfo:
    app = _clean_application(app)
    if not admission_dao.get_by_id(app.application_id):
        raise ValueError(f"Không tìm thấy hồ sơ '{app.application_id}'.")
    _validate_application(app, is_update=True)
    admission_dao.update(app)
    activity_service.log_activity(
        "Cập nhật hồ sơ tuyển sinh",
        f"Cập nhật hồ sơ {app.application_id} - {app.full_name}",
    )
    return app


def delete_application(application_id: str) -> bool:
    existing = admission_dao.get_by_id(application_id)
    if not existing:
        raise ValueError(f"Không tìm thấy hồ sơ '{application_id}'.")
    if existing.status == "Đã nhập học":
        raise ValueError("Không thứ xóa hồ sơ Đã nhập học.")
    ok = admission_dao.delete(application_id)
    if ok:
        activity_service.log_activity(
            "Xóa hồ sơ tuyển sinh",
            f"Xóa hồ sơ {existing.application_id} - {existing.full_name}",
        )
    return ok


def auto_screen_application(application_id: str, pass_score: float = DEFAULT_PASS_SCORE) -> AdmissionApplicationInfo:
    if pass_score < 0 or pass_score > 10:
        raise ValueError("Điểm chuẩn phải từ 0 đến 10.")
    app = admission_dao.get_by_id(application_id)
    if not app:
        raise ValueError(f"Không tìm thấy hồ sơ '{application_id}'.")
    if app.status == "Đã nhập học":
        raise ValueError("Hồ sơ Đã nhập học, không thể xét tuyển lai.")
    if app.admission_score is None:
        raise ValueError("Hồ sơ chưa có điểm xét tuyển.")

    app.status = "Đạt" if app.admission_score >= pass_score else "Không Đạt"
    app.notes = _append_note(app.notes, f"Xét tuyển tự động với điểm chuẩn {pass_score:g}: {app.status}.")
    admission_dao.update(app)
    activity_service.log_activity(
        "Xét tuyển tự động",
        f"Hồ sơ {app.application_id} đạt kết quả {app.status}",
    )
    return app


def auto_screen_all(pass_score: float = DEFAULT_PASS_SCORE) -> int:
    applications = [
        app for app in admission_dao.get_all()
        if app.status in ("Mới", "Đạt", "Không Đạt")
    ]
    for app in applications:
        auto_screen_application(app.application_id, pass_score=pass_score)
    return len(applications)


def enroll_application(application_id: str, class_code: Optional[str] = None) -> HocSinhInfo:
    app = admission_dao.get_by_id(application_id)
    if not app:
        raise ValueError(f"Không tìm thấy hồ sơ '{application_id}'.")
    if app.status != "Đạt":
        raise ValueError("Chi hồ sơ Đạt mới được nhợp học.")
    if app.student_code:
        raise ValueError(f"Hồ sơ đã được cấp mã học sinh {app.student_code}.")

    selected_class = class_code or app.desired_class
    if not selected_class:
        raise ValueError("Cần chọn lớp để phân lớp trước khi nhập học.")
    if not school_class_dao.get_by_id(selected_class):
        raise ValueError(f"Lớp '{selected_class}' không tồn tại.")

    student = HocSinhInfo(
        ma_hs=student_service.generate_next_id(),
        ho_ten=app.full_name,
        gioi_tinh=app.gender,
        ngay_sinh=app.dob,
        dia_chi=app.address,
        diem_tb=app.admission_score,
        ma_lop=selected_class,
        parent_name=app.parent_name,
        parent_phone=app.parent_phone,
        learning_status="Đang học",
        policy_type="Không",
    )
    student_service.create_student(student)

    app.status = "Đã nhập học"
    app.student_code = student.ma_hs
    app.desired_class = selected_class
    app.notes = _append_note(app.notes, f"Nhập học và cấp mã học sinh {student.ma_hs}.")
    admission_dao.update(app)
    activity_service.log_activity(
        "Nhợp học",
        f"Hồ sơ {app.application_id} trở thành học sinh {student.ma_hs}",
    )
    return student


def _append_note(current: Optional[str], addition: str) -> str:
    return f"{current}\n{addition}" if current else addition
