"""SQLAlchemy models for the HSMS web application."""

from app.models.academic import SchoolClass, Student, Teacher, TeacherClassAssignment
from app.models.auth import AccountStatus, ActivityLog, Role, User
from app.models.operations import (
    AdmissionApplication,
    Course,
    CourseSection,
    DiplomaRecord,
    GradeRecord,
    GradeReview,
    GraduationCheck,
    PaymentRecord,
    TuitionInvoice,
)

__all__ = [
    "AccountStatus",
    "ActivityLog",
    "AdmissionApplication",
    "Course",
    "CourseSection",
    "DiplomaRecord",
    "GradeRecord",
    "GradeReview",
    "GraduationCheck",
    "PaymentRecord",
    "Role",
    "SchoolClass",
    "Student",
    "Teacher",
    "TeacherClassAssignment",
    "TuitionInvoice",
    "User",
]
