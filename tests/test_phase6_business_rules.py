from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.auth import Role
from app.models.operations import (
    AdmissionApplication,
    Course,
    CourseRegistration,
    CourseSection,
    GradeReview,
    GraduationCheck,
    PaymentRecord,
    TuitionInvoice,
)
from app.services.admission_web_service import AdmissionWebService
from app.services.auth_service import AuthService
from app.services.business_rule_service import ExamRules, FinanceRules, GraduationRules, ReportRules, TrainingRules
from app.services.mvp_service import ValidationError


@pytest.fixture()
def rule_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        admin = AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        yield app, admin
        db.session.remove()
        db.drop_all()


def test_admissions_capacity_and_double_enrollment(rule_app) -> None:
    app, admin = rule_app
    with app.app_context():
        school_class = SchoolClass(code="C10", name="Lớp 10", capacity=1)
        existing_student = Student(code="S0001", full_name="Có sẵn", school_class=school_class)
        application = AdmissionApplication(
            application_code="TS001",
            full_name="Ứng viên",
            admission_score=Decimal("8"),
            status="approved",
            desired_class=school_class,
        )
        db.session.add_all([school_class, existing_student, application])
        db.session.commit()

        with pytest.raises(ValidationError, match="đủ sĩ số"):
            AdmissionWebService.enroll(application.id, admin)

        school_class.capacity = 2
        db.session.commit()
        AdmissionWebService.enroll(application.id, admin)

        with pytest.raises(ValidationError, match="đã được nhập học"):
            AdmissionWebService.enroll(application.id, admin)


def test_training_registration_and_schedule_guards(rule_app) -> None:
    app, admin = rule_app
    with app.app_context():
        school_class = SchoolClass(code="C11", name="Lớp 11")
        teacher = Teacher(code="GV01", full_name="Giáo viên")
        course = Course(code="MATH", name="Toán", credits=3)
        section = CourseSection(code="SEC01", course=course, school_class=school_class, teacher=teacher, capacity=1)
        other_section = CourseSection(code="SEC02", course=course, school_class=school_class, teacher=teacher, capacity=5)
        student = Student(code="S1001", full_name="Học sinh", school_class=school_class)
        other_student = Student(code="S1002", full_name="Học sinh 2", school_class=school_class)
        db.session.add_all([school_class, teacher, course, section, other_section, student, other_student])
        db.session.commit()

        TrainingRules.register_student(section, student, admin)
        with pytest.raises(ValidationError, match="đã đăng ký"):
            TrainingRules.register_student(section, student, admin)
        with pytest.raises(ValidationError, match="đủ sĩ số"):
            TrainingRules.register_student(section, other_student, admin)

        CourseRegistration.query.filter_by(section_id=section.id, student_id=student.id).one().status = "canceled"
        db.session.commit()
        assert TrainingRules.active_registration_count(section) == 0

        TrainingRules.schedule_section(section, "Thứ 2", 1, 3, "P101", admin)
        with pytest.raises(ValidationError, match="Trùng phòng"):
            TrainingRules.schedule_section(other_section, "Thứ 2", 2, 4, "P101", admin)


def test_exam_score_scope_and_review_update(rule_app) -> None:
    app, admin = rule_app
    with app.app_context():
        school_class = SchoolClass(code="C12", name="Lớp 12")
        course = Course(code="PHY", name="Vật lý", credits=3)
        section = CourseSection(code="SEC03", course=course, school_class=school_class, capacity=5)
        student = Student(code="S2001", full_name="Đúng lớp", school_class=school_class)
        outsider = Student(code="S2002", full_name="Ngoài lớp")
        db.session.add_all([school_class, course, section, student, outsider])
        db.session.commit()

        with pytest.raises(ValidationError, match="miền từ 0 đến 10"):
            ExamRules.save_grade(section, student, Decimal("11"), Decimal("8"), Decimal("8"), admin)

        with pytest.raises(ValidationError, match="không thuộc lớp"):
            ExamRules.save_grade(section, outsider, Decimal("8"), Decimal("8"), Decimal("8"), admin)

        grade = ExamRules.save_grade(section, student, Decimal("7"), Decimal("8"), Decimal("9"), admin)
        review = GradeReview(grade_record=grade, reason="Xin phúc khảo", status="pending")
        db.session.add(review)
        db.session.commit()

        ExamRules.resolve_review(review, Decimal("9.5"), admin)

        assert review.status == "resolved"
        assert grade.final_score == Decimal("9.5")
        assert grade.average10 == Decimal("9.5")


def test_finance_payment_invoice_and_scholarship_guards(rule_app) -> None:
    app, admin = rule_app
    with app.app_context():
        student = Student(code="S3001", full_name="Tài chính")
        invoice = TuitionInvoice(
            invoice_code="HD01",
            student=student,
            term="HK1",
            invoice_type="credit",
            total_amount=Decimal("1000"),
            paid_amount=Decimal("0"),
            status="unpaid",
            due_date=date.today() - timedelta(days=1),
        )
        db.session.add_all([student, invoice])
        db.session.commit()

        FinanceRules.refresh_overdue_status(invoice)
        assert invoice.status == "overdue"

        with pytest.raises(ValidationError, match="số tiền âm"):
            FinanceRules.record_payment(invoice, PaymentRecord(payment_code="P0", invoice_id=invoice.id, amount=Decimal("-1"), method="cash"), admin)

        with pytest.raises(ValidationError, match="vượt số tiền"):
            FinanceRules.record_payment(invoice, PaymentRecord(payment_code="P1", invoice_id=invoice.id, amount=Decimal("1001"), method="cash"), admin)

        payment = PaymentRecord(payment_code="P2", invoice_id=invoice.id, amount=Decimal("500"), method="cash")
        FinanceRules.record_payment(invoice, payment, admin)
        assert invoice.paid_amount == Decimal("500")
        assert invoice.status == "partial"

        with pytest.raises(ValidationError, match="đã có thanh toán"):
            FinanceRules.delete_invoice(invoice, admin)

        with pytest.raises(ValidationError, match="Không có điểm thực tế"):
            FinanceRules.scholarship_average(student)


def test_graduation_and_report_guards(rule_app) -> None:
    app, admin = rule_app
    with app.app_context():
        student = Student(code="S4001", full_name="Tốt nghiệp")
        check = GraduationCheck(
            student=student,
            required_credits=120,
            earned_credits=100,
            informatics_cert=True,
            language_cert=True,
            defense_cert=True,
            status="not_eligible",
        )
        db.session.add_all([student, check])
        db.session.commit()

        with pytest.raises(ValidationError, match="chưa đạt"):
            GraduationRules.issue_diploma(check, "SG001", "B001", admin)

        check.status = "eligible"
        db.session.commit()
        diploma = GraduationRules.issue_diploma(check, "SG001", "B001", admin)
        assert diploma.status == "issued"
        assert check.status == "graduated"

        with pytest.raises(ValidationError, match="đường dẫn giả"):
            ReportRules.require_real_export_template("")
