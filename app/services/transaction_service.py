from __future__ import annotations

from decimal import Decimal
from contextlib import contextmanager

from app.extensions import db
from app.models.academic import SchoolClass, Student
from app.models.auth import User
from app.models.operations import (
    AdmissionApplication,
    DiplomaRecord,
    GradeRecord,
    GradeReview,
    GraduationCheck,
    PaymentRecord,
    TuitionInvoice,
)
from app.services.auth_service import AuthService


class BusinessTransactionService:
    @staticmethod
    @contextmanager
    def transaction():
        session = db.session()
        if session.in_transaction():
            with db.session.begin_nested():
                yield
        else:
            with db.session.begin():
                yield

    @staticmethod
    def enroll_admission(application: AdmissionApplication, student_code: str, actor: User | None = None) -> Student:
        """Admission profile -> official student in one transaction."""

        with BusinessTransactionService.transaction():
            student = Student(
                code=student_code,
                full_name=application.full_name,
                gender=application.gender,
                date_of_birth=application.date_of_birth,
                address=application.address,
                class_id=application.desired_class_id,
                parent_name=application.parent_name,
                parent_phone=application.parent_phone,
                learning_status="Đang học",
            )
            db.session.add(student)
            db.session.flush()
            application.status = "enrolled"
            application.student_id = student.id
            AuthService.log_activity(
                actor,
                "enroll_admission",
                "admissions",
                target_type="student",
                target_id=student.code,
                detail=f"Nhập học từ hồ sơ {application.application_code}",
            )
        return student

    @staticmethod
    def record_payment(invoice: TuitionInvoice, payment: PaymentRecord, actor: User | None = None) -> None:
        """Payment -> update invoice in one transaction."""

        with BusinessTransactionService.transaction():
            db.session.add(payment)
            invoice.paid_amount = Decimal(invoice.paid_amount or 0) + Decimal(payment.amount)
            BusinessTransactionService._refresh_invoice_status(invoice)
            AuthService.log_activity(
                actor,
                "record_payment",
                "finance",
                target_type="invoice",
                target_id=invoice.invoice_code,
                detail=f"Thanh toán {payment.amount}",
            )

    @staticmethod
    def delete_payment(payment: PaymentRecord, actor: User | None = None) -> None:
        """Delete payment -> recalculate invoice in one transaction."""

        with BusinessTransactionService.transaction():
            invoice = payment.invoice
            db.session.delete(payment)
            db.session.flush()
            invoice.paid_amount = sum((Decimal(item.amount) for item in invoice.payments.all()), Decimal("0"))
            BusinessTransactionService._refresh_invoice_status(invoice)
            AuthService.log_activity(
                actor,
                "delete_payment",
                "finance",
                target_type="invoice",
                target_id=invoice.invoice_code,
                detail="Xóa thanh toán và tính lại hóa đơn",
            )

    @staticmethod
    def resolve_grade_review(review: GradeReview, adjusted_score: Decimal, actor: User | None = None) -> None:
        """Grade review -> update grade in one transaction."""

        with BusinessTransactionService.transaction():
            review.status = "resolved"
            review.adjusted_score = adjusted_score
            review.grade_record.final_score = adjusted_score
            AuthService.log_activity(
                actor,
                "resolve_grade_review",
                "exams",
                target_type="grade_review",
                target_id=str(review.id),
                detail="Phúc khảo và cập nhật điểm",
            )

    @staticmethod
    def issue_diploma(
        graduation_check: GraduationCheck,
        registry_no: str,
        diploma_no: str,
        actor: User | None = None,
    ) -> DiplomaRecord:
        """Graduation check -> diploma issue in one transaction."""

        with BusinessTransactionService.transaction():
            graduation_check.status = "graduated"
            diploma = DiplomaRecord(
                student_id=graduation_check.student_id,
                graduation_check_id=graduation_check.id,
                registry_no=registry_no,
                diploma_no=diploma_no,
                status="issued",
            )
            db.session.add(diploma)
            AuthService.log_activity(
                actor,
                "issue_diploma",
                "graduation",
                target_type="student",
                target_id=str(graduation_check.student_id),
                detail=f"Cấp bằng {diploma_no}",
            )
        return diploma

    @staticmethod
    def transfer_student(student: Student, new_class: SchoolClass | None, new_status: str, actor: User | None = None) -> None:
        """Class transfer or student status change in one transaction."""

        with BusinessTransactionService.transaction():
            old_class_id = student.class_id
            old_status = student.learning_status
            student.class_id = new_class.id if new_class else None
            student.learning_status = new_status
            AuthService.log_activity(
                actor,
                "transfer_student",
                "students",
                target_type="student",
                target_id=student.code,
                detail=f"class {old_class_id}->{student.class_id}; status {old_status}->{new_status}",
            )

    @staticmethod
    def _refresh_invoice_status(invoice: TuitionInvoice) -> None:
        if Decimal(invoice.paid_amount or 0) <= 0:
            invoice.status = "unpaid"
        elif Decimal(invoice.paid_amount) < Decimal(invoice.total_amount):
            invoice.status = "partial"
        else:
            invoice.status = "paid"
