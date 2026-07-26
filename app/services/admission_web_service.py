from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.auth import User
from app.models.operations import AdmissionApplication
from app.repositories.admission_repository import AdmissionRepository
from app.repositories.mvp_repository import SchoolClassRepository
from app.services.auth_service import AuthService
from app.services.mvp_service import ValidationError
from app.services.transaction_service import BusinessTransactionService


class AdmissionWebService:
    PASSING_SCORE = Decimal("5.00")

    @staticmethod
    def list(search: str | None = None, status: str | None = None) -> list[AdmissionApplication]:
        return AdmissionRepository.list(search, status)

    @staticmethod
    def receive_application(data: dict, actor: User, application_id: int | None = None) -> AdmissionApplication:
        code = (data.get("application_code") or "").strip() or AdmissionRepository.next_application_code()
        full_name = AdmissionWebService._required(data.get("full_name"), "Họ tên thí sinh")
        admission_score = AdmissionWebService._parse_score(data.get("admission_score"))
        desired_class_id = int(data["desired_class_id"]) if data.get("desired_class_id") else None

        if desired_class_id and not SchoolClassRepository.get(desired_class_id):
            raise ValidationError("Lớp dự kiến không tồn tại.")

        existing = AdmissionRepository.get_by_code(code)
        if existing and existing.id != application_id:
            raise ValidationError("Mã hồ sơ tuyển sinh đã tồn tại.")

        application = AdmissionRepository.get(application_id) if application_id else AdmissionApplication()
        if not application:
            raise ValidationError("Không tìm thấy hồ sơ tuyển sinh.")
        if application.status == "enrolled":
            raise ValidationError("Hồ sơ đã nhập học, không thể chỉnh sửa.")

        application.application_code = code
        application.full_name = full_name
        application.gender = int(data["gender"]) if data.get("gender") not in {None, ""} else None
        application.date_of_birth = AdmissionWebService._parse_date(data.get("date_of_birth"))
        application.address = (data.get("address") or "").strip() or None
        application.phone = (data.get("phone") or "").strip() or None
        application.parent_name = (data.get("parent_name") or "").strip() or None
        application.parent_phone = (data.get("parent_phone") or "").strip() or None
        application.admission_score = admission_score
        application.desired_class_id = desired_class_id
        application.desired_major = (data.get("desired_major") or "").strip() or None
        application.status = data.get("status") or application.status or "pending"
        application.notes = (data.get("notes") or "").strip() or None

        db.session.add(application)
        db.session.commit()
        AuthService.log_activity(
            actor,
            "receive_admission_application",
            "admissions",
            "admission_application",
            application.application_code,
            "Tiếp nhận/cập nhật hồ sơ tuyển sinh",
        )
        return application

    @staticmethod
    def auto_screen(application_id: int, actor: User, passing_score: Decimal | None = None) -> AdmissionApplication:
        application = AdmissionWebService._get_mutable_application(application_id)
        threshold = passing_score or AdmissionWebService.PASSING_SCORE
        if application.admission_score is None:
            raise ValidationError("Hồ sơ chưa có điểm xét tuyển.")

        with BusinessTransactionService.transaction():
            application.status = "approved" if Decimal(application.admission_score) >= threshold else "rejected"
            AuthService.log_activity(
                actor,
                "auto_screen_admission",
                "admissions",
                "admission_application",
                application.application_code,
                f"Điểm chuẩn {threshold}; kết quả {application.status}",
            )
        return application

    @staticmethod
    def enroll(application_id: int, actor: User) -> str:
        application = AdmissionRepository.get(application_id)
        if not application:
            raise ValidationError("Không tìm thấy hồ sơ tuyển sinh.")
        if application.student_id:
            raise ValidationError("Hồ sơ đã được nhập học.")
        if application.status != "approved":
            raise ValidationError("Chỉ hồ sơ đã trúng tuyển mới được nhập học.")
        if application.desired_class and application.desired_class.capacity is not None:
            if application.desired_class.students.count() >= application.desired_class.capacity:
                raise ValidationError("Lớp dự kiến đã đủ sĩ số.")

        student_code = AdmissionRepository.next_student_code()
        BusinessTransactionService.enroll_admission(application, student_code, actor)
        return student_code

    @staticmethod
    def delete(application_id: int, actor: User) -> None:
        application = AdmissionRepository.get(application_id)
        if not application:
            raise ValidationError("Không tìm thấy hồ sơ tuyển sinh.")
        if application.student_id:
            raise ValidationError("Không thể xóa hồ sơ đã nhập học.")

        code = application.application_code
        db.session.delete(application)
        db.session.commit()
        AuthService.log_activity(actor, "delete_admission_application", "admissions", "admission_application", code)

    @staticmethod
    def _get_mutable_application(application_id: int) -> AdmissionApplication:
        application = AdmissionRepository.get(application_id)
        if not application:
            raise ValidationError("Không tìm thấy hồ sơ tuyển sinh.")
        if application.status == "enrolled":
            raise ValidationError("Hồ sơ đã nhập học.")
        return application

    @staticmethod
    def _required(value: str | None, field_name: str) -> str:
        clean = (value or "").strip()
        if not clean:
            raise ValidationError(f"{field_name} không được để trống.")
        return clean

    @staticmethod
    def _parse_score(value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            score = Decimal(value)
        except InvalidOperation as exc:
            raise ValidationError("Điểm xét tuyển không hợp lệ.") from exc
        if score < 0 or score > 10:
            raise ValidationError("Điểm xét tuyển phải từ 0 đến 10.")
        return score

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError("Ngày sinh không hợp lệ.") from exc
