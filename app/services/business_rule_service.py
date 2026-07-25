from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import and_, or_

from app.extensions import db
from app.models.academic import Student
from app.models.auth import User
from app.models.operations import (
    ClassSchedule,
    CourseRegistration,
    CourseSection,
    DiplomaRecord,
    GradeRecord,
    GradeReview,
    GraduationCheck,
    PaymentRecord,
    TuitionInvoice,
)
from app.services.auth_service import AuthService
from app.services.mvp_service import ValidationError
from app.services.transaction_service import BusinessTransactionService


ACTIVE_REGISTRATION_STATUSES = {"active", "registered"}


class AdmissionRules:
    @staticmethod
    def ensure_class_capacity(student: Student) -> None:
        school_class = student.school_class
        if not school_class or school_class.capacity is None:
            return
        if school_class.students.count() > school_class.capacity:
            raise ValidationError("Sĩ số lớp đã vượt cấu hình cho phép.")


class TrainingRules:
    @staticmethod
    def register_student(section: CourseSection, student: Student, actor: User | None = None) -> CourseRegistration:
        existing = CourseRegistration.query.filter_by(section_id=section.id, student_id=student.id).first()
        if existing and existing.status in ACTIVE_REGISTRATION_STATUSES:
            raise ValidationError("Học sinh đã đăng ký học phần này.")
        if section.capacity is not None and TrainingRules.active_registration_count(section) >= section.capacity:
            raise ValidationError("Lớp học phần đã đủ sĩ số.")

        with BusinessTransactionService.transaction():
            if existing:
                existing.status = "active"
                registration = existing
            else:
                registration = CourseRegistration(section_id=section.id, student_id=student.id, status="active")
                db.session.add(registration)
            AuthService.log_activity(
                actor,
                "register_course_section",
                "training",
                "course_section",
                section.code,
                f"Đăng ký học sinh {student.code}",
            )
        return registration

    @staticmethod
    def active_registration_count(section: CourseSection) -> int:
        return CourseRegistration.query.filter(
            CourseRegistration.section_id == section.id,
            CourseRegistration.status.in_(ACTIVE_REGISTRATION_STATUSES),
        ).count()

    @staticmethod
    def schedule_section(
        section: CourseSection,
        weekday: str,
        start_period: int,
        end_period: int,
        room: str,
        actor: User | None = None,
    ) -> ClassSchedule:
        if start_period > end_period:
            raise ValidationError("Tiết bắt đầu phải nhỏ hơn hoặc bằng tiết kết thúc.")

        overlap = TrainingRules._overlap_filter(weekday, start_period, end_period)
        room_conflict = ClassSchedule.query.join(CourseSection).filter(overlap, ClassSchedule.room == room).first()
        if room_conflict:
            raise ValidationError("Trùng phòng học trong cùng khung thời gian.")

        if section.teacher_id:
            teacher_conflict = (
                ClassSchedule.query.join(CourseSection)
                .filter(overlap, CourseSection.teacher_id == section.teacher_id)
                .first()
            )
            if teacher_conflict:
                raise ValidationError("Trùng lịch giáo viên trong cùng khung thời gian.")

        if section.class_id:
            class_conflict = (
                ClassSchedule.query.join(CourseSection)
                .filter(overlap, CourseSection.class_id == section.class_id)
                .first()
            )
            if class_conflict:
                raise ValidationError("Trùng lịch lớp trong cùng khung thời gian.")

        with BusinessTransactionService.transaction():
            schedule = ClassSchedule(
                section_id=section.id,
                weekday=weekday,
                start_period=start_period,
                end_period=end_period,
                room=room,
            )
            db.session.add(schedule)
            AuthService.log_activity(actor, "schedule_course_section", "training", "course_section", section.code)
        return schedule

    @staticmethod
    def _overlap_filter(weekday: str, start_period: int, end_period: int):
        return and_(
            ClassSchedule.weekday == weekday,
            ClassSchedule.start_period <= end_period,
            ClassSchedule.end_period >= start_period,
        )


class ExamRules:
    DEFAULT_WEIGHTS = {"component": Decimal("0.2"), "midterm": Decimal("0.3"), "final": Decimal("0.5")}

    @staticmethod
    def save_grade(
        section: CourseSection,
        student: Student,
        component_score: Decimal,
        midterm_score: Decimal,
        final_score: Decimal,
        actor: User | None = None,
        weights: dict[str, Decimal] | None = None,
    ) -> GradeRecord:
        for score in [component_score, midterm_score, final_score]:
            ExamRules.validate_score(score)
        ExamRules.ensure_student_in_section_scope(section, student)
        selected_weights = weights or ExamRules.DEFAULT_WEIGHTS
        if sum(selected_weights.values(), Decimal("0")) != Decimal("1.0"):
            raise ValidationError("Tổng trọng số điểm phải bằng 1.0.")

        average = (
            component_score * selected_weights["component"]
            + midterm_score * selected_weights["midterm"]
            + final_score * selected_weights["final"]
        )
        with BusinessTransactionService.transaction():
            grade = GradeRecord.query.filter_by(section_id=section.id, student_id=student.id).first()
            if not grade:
                grade = GradeRecord(section_id=section.id, student_id=student.id)
                db.session.add(grade)
            grade.component_score = component_score
            grade.midterm_score = midterm_score
            grade.final_score = final_score
            grade.average10 = average
            grade.gpa4 = min(Decimal("4.0"), average / Decimal("2.5"))
            grade.letter_grade = ExamRules.letter_grade(average)
            AuthService.log_activity(actor, "save_grade", "exams", "grade_record", f"{section.code}:{student.code}")
        return grade

    @staticmethod
    def resolve_review(review: GradeReview, adjusted_score: Decimal, actor: User | None = None) -> None:
        ExamRules.validate_score(adjusted_score)
        with BusinessTransactionService.transaction():
            review.status = "resolved"
            review.adjusted_score = adjusted_score
            review.grade_record.final_score = adjusted_score
            review.grade_record.average10 = adjusted_score
            review.grade_record.gpa4 = min(Decimal("4.0"), adjusted_score / Decimal("2.5"))
            review.grade_record.letter_grade = ExamRules.letter_grade(adjusted_score)
            AuthService.log_activity(
                actor,
                "resolve_grade_review",
                "exams",
                "grade_review",
                str(review.id),
                "Phúc khảo và cập nhật lại kết quả",
            )

    @staticmethod
    def validate_score(score: Decimal) -> None:
        if score < 0 or score > 10:
            raise ValidationError("Điểm phải nằm trong miền từ 0 đến 10.")

    @staticmethod
    def ensure_student_in_section_scope(section: CourseSection, student: Student) -> None:
        if section.class_id and student.class_id == section.class_id:
            return
        active_registration = CourseRegistration.query.filter(
            CourseRegistration.section_id == section.id,
            CourseRegistration.student_id == student.id,
            CourseRegistration.status.in_(ACTIVE_REGISTRATION_STATUSES),
        ).first()
        if active_registration:
            return
        raise ValidationError("Không được nhập điểm cho học sinh không thuộc lớp hoặc học phần.")

    @staticmethod
    def letter_grade(score: Decimal) -> str:
        if score >= Decimal("8.5"):
            return "A"
        if score >= Decimal("7.0"):
            return "B"
        if score >= Decimal("5.5"):
            return "C"
        if score >= Decimal("4.0"):
            return "D"
        return "F"


class FinanceRules:
    @staticmethod
    def record_payment(invoice: TuitionInvoice, payment: PaymentRecord, actor: User | None = None) -> None:
        amount = Decimal(payment.amount)
        if amount <= 0:
            raise ValidationError("Không được thanh toán số tiền âm hoặc bằng 0.")
        remaining = Decimal(invoice.total_amount) - Decimal(invoice.paid_amount or 0)
        if amount > remaining:
            raise ValidationError("Không được thanh toán vượt số tiền còn nợ.")
        payment.invoice_id = invoice.id
        BusinessTransactionService.record_payment(invoice, payment, actor)

    @staticmethod
    def delete_invoice(invoice: TuitionInvoice, actor: User | None = None) -> None:
        if invoice.payments.count() > 0:
            raise ValidationError("Không thể xóa hóa đơn đã có thanh toán nếu chưa xử lý thanh toán liên quan.")
        code = invoice.invoice_code
        with BusinessTransactionService.transaction():
            db.session.delete(invoice)
            AuthService.log_activity(actor, "delete_invoice", "finance", "invoice", code)

    @staticmethod
    def refresh_overdue_status(invoice: TuitionInvoice, today: date | None = None) -> None:
        current_date = today or date.today()
        if invoice.status != "paid" and invoice.due_date and invoice.due_date < current_date:
            invoice.status = "overdue"

    @staticmethod
    def scholarship_average(student: Student) -> Decimal:
        average = db.session.query(db.func.avg(GradeRecord.average10)).filter(
            GradeRecord.student_id == student.id,
            GradeRecord.average10.isnot(None),
        ).scalar()
        if average is None:
            raise ValidationError("Không có điểm thực tế để xét học bổng.")
        return Decimal(str(round(float(average), 2)))


class GraduationRules:
    @staticmethod
    def issue_diploma(
        graduation_check: GraduationCheck,
        registry_no: str,
        diploma_no: str,
        actor: User | None = None,
    ) -> DiplomaRecord:
        if graduation_check.status != "eligible":
            raise ValidationError("Không thể cấp bằng cho học sinh chưa đạt điều kiện tốt nghiệp.")
        if graduation_check.student_id != graduation_check.student.id:
            raise ValidationError("Bản xét tốt nghiệp không thuộc đúng học sinh.")
        if DiplomaRecord.query.filter(
            or_(DiplomaRecord.registry_no == registry_no, DiplomaRecord.diploma_no == diploma_no)
        ).first():
            raise ValidationError("Số bằng hoặc số sổ gốc đã tồn tại.")
        return BusinessTransactionService.issue_diploma(graduation_check, registry_no, diploma_no, actor)


class ReportRules:
    @staticmethod
    def require_real_export_template(template_path: str | None) -> None:
        if not template_path:
            raise ValidationError("Xuất biểu mẫu cần mẫu thật, không tạo đường dẫn giả.")
