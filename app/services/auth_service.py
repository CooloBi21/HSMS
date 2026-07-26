from __future__ import annotations

from dataclasses import dataclass

from flask import has_request_context, request

from app.extensions import db
from app.models.auth import AccountStatus, ActivityLog, Role, User
from app.repositories.auth_repository import ActivityLogRepository, UserRepository


class AuthenticationError(ValueError):
    pass


class AuthorizationError(PermissionError):
    pass


@dataclass(frozen=True)
class Scope:
    student_code: str | None = None
    teacher_code: str | None = None


ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.ADMIN.value: {
        "dashboard:view",
        "activity:view",
        "accounts:manage",
        "students:manage",
        "classes:manage",
        "teachers:manage",
        "admissions:access",
        "profiles:access",
        "training:access",
        "exams:access",
        "finance:access",
        "affairs:access",
        "graduation:access",
        "student:self:view",
        "teacher:assigned:view",
    },
    Role.TEACHER.value: {
        "dashboard:view",
        "classes:assigned:view",
        "students:assigned:view",
        "attendance:manage",
        "grades:assigned:manage",
        "training:assigned:view",
        "exams:assigned:view",
        "teacher:assigned:view",
    },
    Role.STUDENT.value: {
        "profile:self:view",
        "classes:self:view",
        "schedule:self:view",
        "grades:self:view",
        "student:self:view",
    },
}


class AuthService:
    @staticmethod
    def authenticate(username: str, password: str) -> User:
        user = UserRepository.get_by_username(username.strip())
        if not user or not user.check_password(password):
            raise AuthenticationError("Tên đăng nhập hoặc mật khẩu không đúng.")
        if user.status != AccountStatus.ACTIVE.value:
            raise AuthenticationError("Tài khoản không ở trạng thái hoạt động.")
        AuthService.log_activity(user, "login", "auth", detail="Đăng nhập hệ thống")
        return user

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> None:
        if not user.check_password(current_password):
            raise AuthenticationError("Mật khẩu hiện tại không đúng.")
        AuthService.validate_password(new_password)
        user.set_password(new_password)
        user.must_change_password = False
        UserRepository.save(user)
        AuthService.log_activity(user, "change_password", "auth", detail="Đổi mật khẩu")

    @staticmethod
    def create_user(
        username: str,
        full_name: str,
        password: str,
        role: Role,
        actor: User | None = None,
        status: AccountStatus = AccountStatus.ACTIVE,
        email: str | None = None,
        student_code: str | None = None,
        teacher_code: str | None = None,
        student_id: int | None = None,
        teacher_id: int | None = None,
        must_change_password: bool = False,
    ) -> User:
        AuthService.validate_password(password)
        if UserRepository.get_by_username(username):
            raise ValueError("Tên đăng nhập đã tồn tại.")

        user = User(
            username=username.strip(),
            full_name=full_name.strip(),
            email=email,
            role=role.value,
            status=status.value,
            student_code=student_code,
            teacher_code=teacher_code,
            student_id=student_id,
            teacher_id=teacher_id,
            must_change_password=must_change_password,
        )
        user.set_password(password)
        UserRepository.create(user)
        AuthService.log_activity(actor, "create_user", "accounts", target_type="user", target_id=str(user.id))
        return user

    @staticmethod
    def update_role(user: User, new_role: Role, actor: User) -> None:
        AuthService.require_permission(actor, "accounts:manage")
        if new_role.value not in {role.value for role in Role}:
            raise AuthorizationError("Vai trò không hợp lệ.")
        old_role = user.role
        user.role = new_role.value
        UserRepository.save(user)
        AuthService.log_activity(
            actor,
            "update_role",
            "accounts",
            target_type="user",
            target_id=str(user.id),
            detail=f"{old_role} -> {new_role.value}",
        )

    @staticmethod
    def update_status(user: User, status: AccountStatus, actor: User) -> None:
        AuthService.require_permission(actor, "accounts:manage")
        user.status = status.value
        UserRepository.save(user)
        AuthService.log_activity(
            actor,
            "update_account_status",
            "accounts",
            target_type="user",
            target_id=str(user.id),
            detail=status.value,
        )

    @staticmethod
    def has_permission(user: User | None, permission: str) -> bool:
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return permission in ROLE_PERMISSIONS.get(user.role, set())

    @staticmethod
    def require_permission(user: User | None, permission: str) -> None:
        if not AuthService.has_permission(user, permission):
            raise AuthorizationError("Bạn không có quyền thực hiện thao tác này.")

    @staticmethod
    def default_endpoint(user: User) -> str:
        if user.role == Role.STUDENT.value:
            return "students.me"
        if user.role == Role.TEACHER.value:
            return "classes.assigned"
        return "dashboard.index"

    @staticmethod
    def ensure_student_scope(user: User, student_code: str) -> None:
        if user.role == Role.ADMIN.value:
            return
        if user.role == Role.STUDENT.value and user.student_code == student_code:
            return
        raise AuthorizationError("Bạn không có quyền truy cập dữ liệu học sinh này.")

    @staticmethod
    def ensure_teacher_scope(user: User, teacher_code: str) -> None:
        if user.role == Role.ADMIN.value:
            return
        if user.role == Role.TEACHER.value and user.teacher_code == teacher_code:
            return
        raise AuthorizationError("Bạn không có quyền truy cập dữ liệu giáo viên này.")

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự.")
        if password.lower() == password or password.upper() == password:
            raise ValueError("Mật khẩu phải có chữ hoa và chữ thường.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Mật khẩu phải có ít nhất một chữ số.")

    @staticmethod
    def log_activity(
        actor: User | None,
        action: str,
        module: str,
        target_type: str | None = None,
        target_id: str | None = None,
        detail: str | None = None,
    ) -> ActivityLog:
        ip_address = None
        user_agent = None
        if has_request_context():
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
            user_agent = request.headers.get("User-Agent")

        log = ActivityLog(
            actor_id=actor.id if actor else None,
            action=action,
            module=module,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        if db.session().in_transaction():
            db.session.add(log)
            db.session.flush()
            return log
        return ActivityLogRepository.create(log)


def create_initial_admin(username: str, password: str, full_name: str = "System Admin") -> User:
    existing = UserRepository.get_by_username(username)
    if existing:
        return existing
    with db.session.begin_nested():
        user = User(username=username, full_name=full_name, role=Role.ADMIN.value, status=AccountStatus.ACTIVE.value)
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    return user
