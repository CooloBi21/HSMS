from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.auth import Role
from app.models.operations import AdmissionApplication, PaymentRecord, TuitionInvoice
from app.services.auth_service import AuthService
from app.services.transaction_service import BusinessTransactionService


@pytest.fixture()
def database_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_core_schema_has_constraints_indexes_and_foreign_keys(database_app) -> None:
    with database_app.app_context():
        inspector = inspect(db.engine)

        assert {"users", "students", "teachers", "school_classes"}.issubset(set(inspector.get_table_names()))

        student_columns = {column["name"]: column for column in inspector.get_columns("students")}
        assert student_columns["id"]["primary_key"]
        assert "created_at" in student_columns
        assert "updated_at" in student_columns

        student_indexes = {index["name"] for index in inspector.get_indexes("students")}
        assert "ix_students_class_id" in student_indexes
        assert "ix_students_learning_status" in student_indexes

        student_uniques = {constraint["name"] for constraint in inspector.get_unique_constraints("students")}
        assert "uq_students_code" in student_uniques

        student_fk_targets = {
            fk["referred_table"]
            for fk in inspector.get_foreign_keys("students")
        }
        assert "school_classes" in student_fk_targets


def test_account_student_teacher_relationships(database_app) -> None:
    with database_app.app_context():
        school_class = SchoolClass(code="C10A1", name="Lớp 10A1", grade_level="10")
        student = Student(code="S0001", full_name="Nguyễn Văn A", school_class=school_class)
        teacher = Teacher(code="GV001", full_name="Trần Thị B", email="teacher@example.local")
        db.session.add_all([school_class, student, teacher])
        db.session.commit()

        student_user = AuthService.create_user(
            "student1",
            "Nguyễn Văn A",
            "Student123",
            Role.STUDENT,
            student_code=student.code,
            student_id=student.id,
        )
        teacher_user = AuthService.create_user(
            "teacher1",
            "Trần Thị B",
            "Teacher123",
            Role.TEACHER,
            teacher_code=teacher.code,
            teacher_id=teacher.id,
        )

        assert student_user.student.code == "S0001"
        assert teacher_user.teacher.code == "GV001"


def test_admission_enrollment_is_transactional(database_app) -> None:
    with database_app.app_context():
        school_class = SchoolClass(code="C11A1", name="Lớp 11A1", grade_level="11")
        app_record = AdmissionApplication(
            application_code="ADM0001",
            full_name="Lê Minh C",
            desired_class=school_class,
            status="approved",
        )
        db.session.add_all([school_class, app_record])
        db.session.commit()

        student = BusinessTransactionService.enroll_admission(app_record, "S9001")

        assert student.id is not None
        assert app_record.status == "enrolled"
        assert app_record.student_id == student.id


def test_payment_updates_invoice_in_one_transaction(database_app) -> None:
    with database_app.app_context():
        student = Student(code="S9002", full_name="Phạm Thanh D")
        invoice = TuitionInvoice(
            invoice_code="HD9002",
            student=student,
            term="HK1 2026",
            invoice_type="credit",
            total_amount=Decimal("1000000"),
            paid_amount=Decimal("0"),
            status="unpaid",
        )
        db.session.add_all([student, invoice])
        db.session.commit()

        payment = PaymentRecord(
            payment_code="TT9002",
            invoice_id=invoice.id,
            amount=Decimal("400000"),
            method="bank_transfer",
            transaction_ref="TX9002",
        )
        BusinessTransactionService.record_payment(invoice, payment)

        assert invoice.paid_amount == Decimal("400000")
        assert invoice.status == "partial"
