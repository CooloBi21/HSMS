from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Role(StrEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    LOCKED = "locked"
    DISABLED = "disabled"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default=AccountStatus.ACTIVE.value, index=True)
    student_code = db.Column(db.String(30), nullable=True, index=True)
    teacher_code = db.Column(db.String(30), nullable=True, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="SET NULL"), unique=True, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), unique=True, nullable=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    activity_logs = db.relationship("ActivityLog", back_populates="actor", lazy="dynamic")
    student = db.relationship("Student", back_populates="user_account")
    teacher = db.relationship("Teacher", back_populates="user_account")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:  # type: ignore[override]
        return self.status == AccountStatus.ACTIVE.value

    def has_role(self, *roles: Role | str) -> bool:
        allowed = {role.value if isinstance(role, Role) else role for role in roles}
        return self.role in allowed


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(120), nullable=False)
    module = db.Column(db.String(80), nullable=False)
    target_type = db.Column(db.String(80), nullable=True)
    target_id = db.Column(db.String(80), nullable=True)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(80), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    actor = db.relationship("User", back_populates="activity_logs")
