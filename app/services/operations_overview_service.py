from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.operations import (
    ClassSchedule,
    Course,
    CourseRegistration,
    CourseSection,
    GradeRecord,
    GradeReview,
    PaymentRecord,
    TuitionInvoice,
)


def _money(value: Decimal | int | float | None) -> float:
    return float(value or 0)


class TrainingOverviewService:
    @staticmethod
    def overview() -> dict:
        registrations = CourseRegistration.query.filter(CourseRegistration.status == "active").count()
        sections = (
            CourseSection.query.outerjoin(Course)
            .outerjoin(Teacher)
            .outerjoin(SchoolClass)
            .order_by(CourseSection.code)
            .limit(12)
            .all()
        )
        schedules = ClassSchedule.query.order_by(ClassSchedule.weekday, ClassSchedule.start_period).limit(12).all()
        return {
            "summary": {
                "courses": Course.query.count(),
                "sections": CourseSection.query.count(),
                "registrations": registrations,
                "schedules": ClassSchedule.query.count(),
            },
            "sections": sections,
            "schedules": schedules,
        }


class ExamOverviewService:
    @staticmethod
    def overview() -> dict:
        average = db.session.query(func.avg(GradeRecord.average10)).scalar()
        grade_rows = (
            db.session.query(GradeRecord.letter_grade, func.count(GradeRecord.id))
            .filter(GradeRecord.letter_grade.isnot(None))
            .group_by(GradeRecord.letter_grade)
            .order_by(GradeRecord.letter_grade)
            .all()
        )
        records = (
            GradeRecord.query.join(Student, GradeRecord.student_id == Student.id)
            .join(CourseSection, GradeRecord.section_id == CourseSection.id)
            .join(Course, CourseSection.course_id == Course.id)
            .order_by(Student.code, Course.code)
            .limit(12)
            .all()
        )
        return {
            "summary": {
                "grade_records": GradeRecord.query.count(),
                "average10": round(float(average), 2) if average is not None else 0,
                "reviews_pending": GradeReview.query.filter(GradeReview.status == "pending").count(),
                "students_with_scores": db.session.query(func.count(func.distinct(GradeRecord.student_id))).scalar() or 0,
            },
            "grade_distribution": grade_rows,
            "records": records,
        }


class FinanceOverviewService:
    @staticmethod
    def overview() -> dict:
        total = db.session.query(func.sum(TuitionInvoice.total_amount)).scalar()
        paid = db.session.query(func.sum(TuitionInvoice.paid_amount)).scalar()
        overdue = TuitionInvoice.query.filter(TuitionInvoice.status == "overdue").count()
        invoices = (
            TuitionInvoice.query.join(Student, TuitionInvoice.student_id == Student.id)
            .order_by(TuitionInvoice.invoice_code)
            .limit(12)
            .all()
        )
        return {
            "summary": {
                "invoices": TuitionInvoice.query.count(),
                "total_amount": _money(total),
                "paid_amount": _money(paid),
                "debt_amount": max(_money(total) - _money(paid), 0),
                "overdue": overdue,
                "payments": PaymentRecord.query.count(),
            },
            "invoices": invoices,
        }
