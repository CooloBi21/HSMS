from __future__ import annotations

import re

from app.extensions import db
from app.models.academic import Student
from app.models.auth import User
from app.repositories.mvp_repository import SchoolClassRepository
from app.repositories.profile_repository import StudentProfileRepository
from app.services.auth_service import AuthService
from app.services.mvp_service import ValidationError
from app.services.transaction_service import BusinessTransactionService


LEARNING_STATUSES = {"Đang học", "Bảo lưu", "Thôi học", "Tốt nghiệp"}
POLICY_TYPES = {"", "Miễn giảm học phí", "Hộ nghèo", "Vùng sâu vùng xa", "Khác"}
PHONE_PATTERN = re.compile(r"^[0-9+\-\s]{8,20}$")


class StudentProfileService:
    @staticmethod
    def list(search: str | None = None, status: str | None = None, policy_type: str | None = None) -> list[Student]:
        return StudentProfileRepository.list(search, status, policy_type)

    @staticmethod
    def get(student_id: int) -> Student:
        student = StudentProfileRepository.get(student_id)
        if not student:
            raise ValidationError("Không tìm thấy hồ sơ học sinh.")
        return student

    @staticmethod
    def update_profile(student_id: int, data: dict, actor: User) -> Student:
        student = StudentProfileService.get(student_id)
        full_name = (data.get("full_name") or "").strip()
        if not full_name:
            raise ValidationError("Họ tên không được để trống.")

        learning_status = (data.get("learning_status") or "Đang học").strip()
        if learning_status not in LEARNING_STATUSES:
            raise ValidationError("Trạng thái học tập không hợp lệ.")

        policy_type = (data.get("policy_type") or "").strip()
        if policy_type not in POLICY_TYPES:
            raise ValidationError("Diện chính sách không hợp lệ.")

        parent_phone = (data.get("parent_phone") or "").strip()
        if parent_phone and not PHONE_PATTERN.match(parent_phone):
            raise ValidationError("Số điện thoại phụ huynh không hợp lệ.")

        class_id = int(data["class_id"]) if data.get("class_id") else None
        new_class = SchoolClassRepository.get(class_id) if class_id else None
        if class_id and not new_class:
            raise ValidationError("Lớp học không tồn tại.")

        with BusinessTransactionService.transaction():
            student.full_name = full_name
            student.gender = int(data["gender"]) if data.get("gender") not in {None, ""} else None
            student.address = (data.get("address") or "").strip() or None
            student.household = (data.get("household") or "").strip() or None
            student.parent_name = (data.get("parent_name") or "").strip() or None
            student.parent_phone = parent_phone or None
            student.policy_type = policy_type or None
            if student.class_id != class_id or student.learning_status != learning_status:
                old_class = student.class_id
                old_status = student.learning_status
                student.class_id = class_id
                student.learning_status = learning_status
                AuthService.log_activity(
                    actor,
                    "update_student_profile_scope",
                    "profiles",
                    "student",
                    student.code,
                    f"class {old_class}->{student.class_id}; status {old_status}->{learning_status}",
                )
            AuthService.log_activity(
                actor,
                "update_student_profile",
                "profiles",
                "student",
                student.code,
                "Cập nhật lý lịch, liên hệ phụ huynh, trạng thái hoặc diện chính sách",
            )
        return student

    @staticmethod
    def get_self_profile(user: User) -> Student:
        if not user.student_id:
            raise ValidationError("Tài khoản chưa liên kết hồ sơ học sinh.")
        student = StudentProfileService.get(user.student_id)
        AuthService.ensure_student_scope(user, student.code)
        return student
