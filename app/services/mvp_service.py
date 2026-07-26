from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.auth import AccountStatus, Role, User
from app.repositories.mvp_repository import (
    AccountRepository,
    DashboardRepository,
    SchoolClassRepository,
    StudentRepository,
    TeacherRepository,
)
from app.services.auth_service import AuthService


class ValidationError(ValueError):
    pass


def _required(value: str | None, field_name: str) -> str:
    clean = (value or "").strip()
    if not clean:
        raise ValidationError(f"{field_name} không được để trống.")
    return clean


class DashboardService:
    @staticmethod
    def overview() -> dict:
        summary = DashboardRepository.summary()
        avg = summary["average_score"]
        return {
            "summary": {
                **summary,
                "average_score": round(float(avg), 2) if avg is not None else 0,
            },
            "academic_distribution": DashboardRepository.academic_distribution(),
            "students_by_class": DashboardRepository.students_by_class(),
            "recent_activity": DashboardRepository.recent_activity(),
            "warnings": DashboardRepository.data_warnings(),
        }


class SchoolClassService:
    @staticmethod
    def list(grade_level: str | None = None) -> list[SchoolClass]:
        return SchoolClassRepository.list(grade_level)

    @staticmethod
    def save(data: dict, actor: User, class_id: int | None = None) -> SchoolClass:
        code = _required(data.get("code"), "Mã lớp")
        name = _required(data.get("name"), "Tên lớp")
        grade_level = (data.get("grade_level") or "").strip() or None

        existing = SchoolClassRepository.get_by_code(code)
        if existing and existing.id != class_id:
            raise ValidationError("Mã lớp đã tồn tại.")

        school_class = SchoolClassRepository.get(class_id) if class_id else SchoolClass()
        if not school_class:
            raise ValidationError("Không tìm thấy lớp học.")

        school_class.code = code
        school_class.name = name
        school_class.grade_level = grade_level
        db.session.add(school_class)
        db.session.commit()
        AuthService.log_activity(actor, "save_class", "classes", "school_class", school_class.code)
        return school_class

    @staticmethod
    def delete(class_id: int, actor: User) -> None:
        school_class = SchoolClassRepository.get(class_id)
        if not school_class:
            raise ValidationError("Không tìm thấy lớp học.")
        if school_class.students.count() > 0:
            raise ValidationError("Không thể xóa lớp còn học sinh.")
        db.session.delete(school_class)
        db.session.commit()
        AuthService.log_activity(actor, "delete_class", "classes", "school_class", school_class.code)


class StudentService:
    @staticmethod
    def list(search: str | None, class_id: int | None, page: int, per_page: int = 12):
        return StudentRepository.list(search, class_id, page, per_page)

    @staticmethod
    def save(data: dict, actor: User, student_id: int | None = None) -> Student:
        code = _required(data.get("code"), "Mã học sinh")
        full_name = _required(data.get("full_name"), "Họ tên")
        class_id = int(data["class_id"]) if data.get("class_id") else None
        average_score = StudentService._parse_score(data.get("average_score"))

        existing = StudentRepository.get_by_code(code)
        if existing and existing.id != student_id:
            raise ValidationError("Mã học sinh đã tồn tại.")
        if class_id and not SchoolClassRepository.get(class_id):
            raise ValidationError("Lớp học không tồn tại.")

        student = StudentRepository.get(student_id) if student_id else Student()
        if not student:
            raise ValidationError("Không tìm thấy học sinh.")

        student.code = code
        student.full_name = full_name
        student.gender = int(data["gender"]) if data.get("gender") not in {None, ""} else None
        student.address = (data.get("address") or "").strip() or None
        student.average_score = average_score
        student.class_id = class_id
        student.learning_status = (data.get("learning_status") or "Đang học").strip()
        db.session.add(student)
        db.session.commit()
        AuthService.log_activity(actor, "save_student", "students", "student", student.code)
        return student

    @staticmethod
    def delete(student_id: int, actor: User) -> None:
        student = StudentRepository.get(student_id)
        if not student:
            raise ValidationError("Không tìm thấy học sinh.")
        if student.user_account:
            raise ValidationError("Không thể xóa học sinh đang có tài khoản liên kết.")
        db.session.delete(student)
        db.session.commit()
        AuthService.log_activity(actor, "delete_student", "students", "student", student.code)

    @staticmethod
    def _parse_score(value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            score = Decimal(value)
        except InvalidOperation as exc:
            raise ValidationError("Điểm trung bình không hợp lệ.") from exc
        if score < 0 or score > 10:
            raise ValidationError("Điểm trung bình phải từ 0 đến 10.")
        return score


class TeacherService:
    PHONE_PATTERN = re.compile(r"^[0-9+\-\s]{8,20}$")

    @staticmethod
    def list(status: str | None = None) -> list[Teacher]:
        return TeacherRepository.list(status)

    @staticmethod
    def save(data: dict, actor: User, teacher_id: int | None = None) -> Teacher:
        code = _required(data.get("code"), "Mã giáo viên")
        full_name = _required(data.get("full_name"), "Họ tên")
        email = (data.get("email") or "").strip() or None
        phone = (data.get("phone") or "").strip() or None

        if email and "@" not in email:
            raise ValidationError("Email không hợp lệ.")
        if phone and not TeacherService.PHONE_PATTERN.match(phone):
            raise ValidationError("Số điện thoại không hợp lệ.")

        existing_code = TeacherRepository.get_by_code(code)
        if existing_code and existing_code.id != teacher_id:
            raise ValidationError("Mã giáo viên đã tồn tại.")
        existing_email = TeacherRepository.get_by_email(email) if email else None
        if existing_email and existing_email.id != teacher_id:
            raise ValidationError("Email giáo viên đã tồn tại.")

        teacher = TeacherRepository.get(teacher_id) if teacher_id else Teacher()
        if not teacher:
            raise ValidationError("Không tìm thấy giáo viên.")

        teacher.code = code
        teacher.full_name = full_name
        teacher.email = email
        teacher.phone = phone
        teacher.subject = (data.get("subject") or "").strip() or None
        teacher.status = (data.get("status") or "active").strip()
        db.session.add(teacher)
        db.session.commit()
        AuthService.log_activity(actor, "save_teacher", "teachers", "teacher", teacher.code)
        return teacher

    @staticmethod
    def delete(teacher_id: int, actor: User) -> None:
        teacher = TeacherRepository.get(teacher_id)
        if not teacher:
            raise ValidationError("Không tìm thấy giáo viên.")
        if teacher.user_account or teacher.sections.count() > 0 or teacher.class_assignments.count() > 0:
            raise ValidationError("Không thể xóa giáo viên đang có liên kết.")
        db.session.delete(teacher)
        db.session.commit()
        AuthService.log_activity(actor, "delete_teacher", "teachers", "teacher", teacher.code)


class AccountService:
    @staticmethod
    def list() -> list[User]:
        return AccountRepository.list()

    @staticmethod
    def save(data: dict, actor: User) -> User:
        AuthService.require_permission(actor, "accounts:manage")
        role = Role(data.get("role"))
        status = AccountStatus(data.get("status") or AccountStatus.ACTIVE.value)
        password = _required(data.get("password"), "Mật khẩu")
        user = AuthService.create_user(
            username=_required(data.get("username"), "Tên đăng nhập"),
            full_name=_required(data.get("full_name"), "Họ tên"),
            password=password,
            role=role,
            actor=actor,
            status=status,
            email=(data.get("email") or "").strip() or None,
        )
        return user

    @staticmethod
    def update_status(user_id: int, status_value: str, actor: User) -> None:
        AuthService.require_permission(actor, "accounts:manage")
        user = AccountRepository.get(user_id)
        if not user:
            raise ValidationError("Không tìm thấy tài khoản.")
        if user.id == actor.id and status_value != AccountStatus.ACTIVE.value:
            raise ValidationError("Không thể tự khóa hoặc vô hiệu hóa tài khoản đang đăng nhập.")
        status = AccountStatus(status_value)
        AuthService.update_status(user, status, actor)
