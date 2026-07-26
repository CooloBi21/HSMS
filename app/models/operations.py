from __future__ import annotations

from app.extensions import db
from app.models.academic import TimestampMixin


class AdmissionApplication(TimestampMixin, db.Model):
    __tablename__ = "admission_applications"
    __table_args__ = (
        db.UniqueConstraint("application_code", name="uq_admission_applications_code"),
        db.Index("ix_admission_applications_status", "status"),
        db.Index("ix_admission_applications_desired_class", "desired_class_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    application_code = db.Column(db.String(30), nullable=False)
    full_name = db.Column(db.String(160), nullable=False)
    gender = db.Column(db.Integer, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    parent_name = db.Column(db.String(160), nullable=True)
    parent_phone = db.Column(db.String(40), nullable=True)
    admission_score = db.Column(db.Numeric(5, 2), nullable=True)
    desired_class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True)
    desired_major = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="pending")
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    desired_class = db.relationship("SchoolClass")
    student = db.relationship("Student", back_populates="admissions")


class Course(TimestampMixin, db.Model):
    __tablename__ = "courses"
    __table_args__ = (
        db.UniqueConstraint("code", name="uq_courses_code"),
        db.Index("ix_courses_grade_level", "grade_level"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    grade_level = db.Column(db.String(20), nullable=True)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    description = db.Column(db.Text, nullable=True)

    prerequisite = db.relationship("Course", remote_side=[id])
    sections = db.relationship("CourseSection", back_populates="course", lazy="dynamic")


class CourseSection(TimestampMixin, db.Model):
    __tablename__ = "course_sections"
    __table_args__ = (
        db.Index("ix_course_sections_course", "course_id"),
        db.Index("ix_course_sections_teacher", "teacher_id"),
        db.Index("ix_course_sections_class", "class_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(40), nullable=False, default="open")

    course = db.relationship("Course", back_populates="sections")
    school_class = db.relationship("SchoolClass", back_populates="sections")
    teacher = db.relationship("Teacher", back_populates="sections")
    grades = db.relationship("GradeRecord", back_populates="section", lazy="dynamic")
    registrations = db.relationship("CourseRegistration", back_populates="section", lazy="dynamic")
    schedules = db.relationship("ClassSchedule", back_populates="section", lazy="dynamic")


class CourseRegistration(TimestampMixin, db.Model):
    __tablename__ = "course_registrations"
    __table_args__ = (
        db.UniqueConstraint("section_id", "student_id", name="uq_course_registrations_scope"),
        db.Index("ix_course_registrations_section", "section_id"),
        db.Index("ix_course_registrations_student", "student_id"),
        db.Index("ix_course_registrations_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("course_sections.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="active")

    section = db.relationship("CourseSection", back_populates="registrations")
    student = db.relationship("Student")


class ClassSchedule(TimestampMixin, db.Model):
    __tablename__ = "class_schedules"
    __table_args__ = (
        db.Index("ix_class_schedules_section", "section_id"),
        db.Index("ix_class_schedules_room_slot", "weekday", "start_period", "end_period", "room"),
    )

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("course_sections.id", ondelete="CASCADE"), nullable=False)
    weekday = db.Column(db.String(20), nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    room = db.Column(db.String(80), nullable=False)

    section = db.relationship("CourseSection", back_populates="schedules")


class TuitionInvoice(TimestampMixin, db.Model):
    __tablename__ = "tuition_invoices"
    __table_args__ = (
        db.Index("ix_tuition_invoices_student", "student_id"),
        db.Index("ix_tuition_invoices_status", "status"),
        db.UniqueConstraint("student_id", "term", "invoice_type", name="uq_tuition_invoice_scope"),
    )

    id = db.Column(db.Integer, primary_key=True)
    invoice_code = db.Column(db.String(30), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    term = db.Column(db.String(40), nullable=False)
    invoice_type = db.Column(db.String(40), nullable=False)
    credit_count = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=True)
    fixed_amount = db.Column(db.Numeric(12, 2), nullable=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(40), nullable=False, default="unpaid")
    due_date = db.Column(db.Date, nullable=True)

    student = db.relationship("Student", back_populates="tuition_invoices")
    payments = db.relationship("PaymentRecord", back_populates="invoice", lazy="dynamic", cascade="all, delete-orphan")


class PaymentRecord(TimestampMixin, db.Model):
    __tablename__ = "payment_records"
    __table_args__ = (
        db.Index("ix_payment_records_invoice", "invoice_id"),
        db.UniqueConstraint("transaction_ref", name="uq_payment_records_transaction_ref"),
    )

    id = db.Column(db.Integer, primary_key=True)
    payment_code = db.Column(db.String(30), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("tuition_invoices.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    method = db.Column(db.String(60), nullable=False)
    transaction_ref = db.Column(db.String(120), nullable=True)
    payment_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    invoice = db.relationship("TuitionInvoice", back_populates="payments")


class GradeRecord(TimestampMixin, db.Model):
    __tablename__ = "grade_records"
    __table_args__ = (
        db.UniqueConstraint("section_id", "student_id", name="uq_grade_records_scope"),
        db.Index("ix_grade_records_section", "section_id"),
        db.Index("ix_grade_records_student", "student_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("course_sections.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    component_score = db.Column(db.Numeric(4, 2), nullable=True)
    midterm_score = db.Column(db.Numeric(4, 2), nullable=True)
    final_score = db.Column(db.Numeric(4, 2), nullable=True)
    average10 = db.Column(db.Numeric(4, 2), nullable=True)
    gpa4 = db.Column(db.Numeric(3, 2), nullable=True)
    letter_grade = db.Column(db.String(5), nullable=True)

    section = db.relationship("CourseSection", back_populates="grades")
    student = db.relationship("Student", back_populates="grade_records")
    reviews = db.relationship("GradeReview", back_populates="grade_record", lazy="dynamic", cascade="all, delete-orphan")


class GradeReview(TimestampMixin, db.Model):
    __tablename__ = "grade_reviews"
    __table_args__ = (db.Index("ix_grade_reviews_status", "status"),)

    id = db.Column(db.Integer, primary_key=True)
    grade_record_id = db.Column(db.Integer, db.ForeignKey("grade_records.id", ondelete="CASCADE"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="pending")
    adjusted_score = db.Column(db.Numeric(4, 2), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    grade_record = db.relationship("GradeRecord", back_populates="reviews")


class GraduationCheck(TimestampMixin, db.Model):
    __tablename__ = "graduation_checks"
    __table_args__ = (
        db.Index("ix_graduation_checks_student", "student_id"),
        db.Index("ix_graduation_checks_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    required_credits = db.Column(db.Integer, nullable=False)
    earned_credits = db.Column(db.Integer, nullable=False)
    informatics_cert = db.Column(db.Boolean, nullable=False, default=False)
    language_cert = db.Column(db.Boolean, nullable=False, default=False)
    defense_cert = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(40), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    student = db.relationship("Student", back_populates="graduation_checks")
    diploma = db.relationship("DiplomaRecord", back_populates="graduation_check", uselist=False)


class DiplomaRecord(TimestampMixin, db.Model):
    __tablename__ = "diploma_records"
    __table_args__ = (
        db.UniqueConstraint("registry_no", name="uq_diploma_records_registry_no"),
        db.UniqueConstraint("diploma_no", name="uq_diploma_records_diploma_no"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    graduation_check_id = db.Column(db.Integer, db.ForeignKey("graduation_checks.id", ondelete="SET NULL"), nullable=True)
    registry_no = db.Column(db.String(80), nullable=False)
    diploma_no = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="issued")
    notes = db.Column(db.Text, nullable=True)

    graduation_check = db.relationship("GraduationCheck", back_populates="diploma")
