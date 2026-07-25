from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class SchoolClass(TimestampMixin, db.Model):
    __tablename__ = "school_classes"
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_school_classes_code"),
        db.Index("ix_school_classes_grade_level", "grade_level"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    grade_level = db.Column(db.String(20), nullable=True)
    homeroom_teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)

    students = db.relationship("Student", back_populates="school_class", lazy="dynamic")
    homeroom_teacher = db.relationship("Teacher", foreign_keys=[homeroom_teacher_id], post_update=True)
    sections = db.relationship("CourseSection", back_populates="school_class", lazy="dynamic")


class Student(TimestampMixin, db.Model):
    __tablename__ = "students"
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_students_code"),
        db.Index("ix_students_class_id", "class_id"),
        db.Index("ix_students_learning_status", "learning_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    full_name = db.Column(db.String(160), nullable=False)
    gender = db.Column(db.Integer, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    average_score = db.Column(db.Numeric(4, 2), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True)
    household = db.Column(db.String(255), nullable=True)
    parent_name = db.Column(db.String(160), nullable=True)
    parent_phone = db.Column(db.String(40), nullable=True)
    learning_status = db.Column(db.String(40), nullable=False, default="Đang học")
    policy_type = db.Column(db.String(80), nullable=True)

    school_class = db.relationship("SchoolClass", back_populates="students")
    user_account = db.relationship("User", back_populates="student", uselist=False)
    admissions = db.relationship("AdmissionApplication", back_populates="student", lazy="dynamic")
    tuition_invoices = db.relationship("TuitionInvoice", back_populates="student", lazy="dynamic")
    grade_records = db.relationship("GradeRecord", back_populates="student", lazy="dynamic")
    graduation_checks = db.relationship("GraduationCheck", back_populates="student", lazy="dynamic")


class Teacher(TimestampMixin, db.Model):
    __tablename__ = "teachers"
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_teachers_code"),
        db.UniqueConstraint("email", name="uq_teachers_email"),
        db.Index("ix_teachers_subject", "subject"),
        db.Index("ix_teachers_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    full_name = db.Column(db.String(160), nullable=False)
    gender = db.Column(db.Integer, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(160), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="active")

    user_account = db.relationship("User", back_populates="teacher", uselist=False)
    sections = db.relationship("CourseSection", back_populates="teacher", lazy="dynamic")
    class_assignments = db.relationship("TeacherClassAssignment", back_populates="teacher", lazy="dynamic")


class TeacherClassAssignment(TimestampMixin, db.Model):
    __tablename__ = "teacher_class_assignments"
    __table_args__ = (
        db.UniqueConstraint("teacher_id", "class_id", "term", name="uq_teacher_class_assignments_scope"),
        db.Index("ix_teacher_class_assignments_teacher", "teacher_id"),
        db.Index("ix_teacher_class_assignments_class", "class_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False)
    term = db.Column(db.String(40), nullable=False)
    role = db.Column(db.String(80), nullable=False, default="subject_teacher")

    teacher = db.relationship("Teacher", back_populates="class_assignments")
    school_class = db.relationship("SchoolClass")
