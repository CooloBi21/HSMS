from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.operations import (
    AdmissionApplication,
    ClassSchedule,
    Course,
    CourseRegistration,
    CourseSection,
    GradeRecord,
    PaymentRecord,
    TuitionInvoice,
)


@dataclass(frozen=True)
class DemoSeedSummary:
    classes: int
    teachers: int
    students: int
    courses: int
    sections: int
    registrations: int
    schedules: int
    grades: int
    invoices: int
    payments: int
    admissions: int


class DemoSeedService:
    FIRST_NAMES = [
        "An",
        "Bình",
        "Chi",
        "Dũng",
        "Giang",
        "Hà",
        "Khánh",
        "Linh",
        "Minh",
        "Ngọc",
        "Phúc",
        "Quân",
        "Trang",
        "Vy",
        "Yến",
    ]
    MIDDLE_NAMES = [
        "Anh",
        "Bảo",
        "Cẩm",
        "Đức",
        "Gia",
        "Hoàng",
        "Kim",
        "Mai",
        "Nhật",
        "Thanh",
    ]
    FAMILY_NAMES = [
        "Nguyễn",
        "Trần",
        "Lê",
        "Phạm",
        "Hoàng",
        "Vũ",
        "Đặng",
        "Bùi",
        "Đỗ",
        "Hồ",
    ]
    SUBJECTS = [
        "Toán",
        "Ngữ văn",
        "Tiếng Anh",
        "Vật lý",
        "Hóa học",
        "Sinh học",
        "Lịch sử",
        "Địa lý",
        "Tin học",
        "Giáo dục công dân",
        "Công nghệ",
        "Giáo dục thể chất",
    ]
    WEEKDAYS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
    POLICY_TYPES = [None, "Miễn giảm học phí", "Hộ nghèo", "Vùng sâu vùng xa", "Con thương binh"]

    @classmethod
    def seed(cls) -> DemoSeedSummary:
        classes = cls._seed_classes()
        teachers = cls._seed_teachers()
        courses = cls._seed_courses()
        students = cls._seed_students(classes[:12])
        sections = cls._seed_sections(classes[:12], teachers, courses)
        schedules = cls._seed_schedules(sections)
        registrations = cls._seed_registrations(students, sections)
        grades = cls._seed_grades(students, sections)
        invoices, payments = cls._seed_finance(students)
        admissions = cls._seed_admissions(classes[:4])
        db.session.commit()
        return DemoSeedSummary(
            classes=len(classes),
            teachers=len(teachers),
            students=len(students),
            courses=len(courses),
            sections=len(sections),
            registrations=registrations,
            schedules=schedules,
            grades=grades,
            invoices=invoices,
            payments=payments,
            admissions=admissions,
        )

    @classmethod
    def _seed_classes(cls) -> list[SchoolClass]:
        classes: list[SchoolClass] = []
        for index in range(1, 23):
            grade = 10 + ((index - 1) % 3)
            code = f"DEMO{grade}A{index:02d}"
            school_class = SchoolClass.query.filter_by(code=code).first()
            if not school_class:
                school_class = SchoolClass(
                    code=code,
                    name=f"Lớp {grade}A{index:02d}",
                    grade_level=str(grade),
                    capacity=45,
                )
                db.session.add(school_class)
            classes.append(school_class)
        db.session.flush()
        return classes

    @classmethod
    def _seed_teachers(cls) -> list[Teacher]:
        teachers: list[Teacher] = []
        for index in range(1, 101):
            code = f"GVDEMO{index:03d}"
            teacher = Teacher.query.filter_by(code=code).first()
            if not teacher:
                teacher = Teacher(
                    code=code,
                    full_name=f"{cls.FAMILY_NAMES[index % 10]} {cls.MIDDLE_NAMES[index % 10]} {cls.FIRST_NAMES[index % 15]}",
                    gender=index % 2,
                    date_of_birth=date(1980 + (index % 18), 1 + (index % 12), 1 + (index % 27)),
                    phone=f"09{index:08d}",
                    email=f"gv.demo{index:03d}@hsms.local",
                    address=f"{10 + index} Đường Giáo viên, Quận {1 + index % 12}",
                    subject=cls.SUBJECTS[(index - 1) % len(cls.SUBJECTS)],
                    status="active" if index % 11 else "on_leave",
                )
                db.session.add(teacher)
            teachers.append(teacher)
        db.session.flush()
        return teachers

    @classmethod
    def _seed_courses(cls) -> list[Course]:
        courses: list[Course] = []
        for index, subject in enumerate(cls.SUBJECTS, start=1):
            code = f"MHDEMO{index:03d}"
            course = Course.query.filter_by(code=code).first()
            if not course:
                course = Course(
                    code=code,
                    name=subject,
                    credits=2 + (index % 3),
                    grade_level=str(10 + ((index - 1) % 3)),
                    description=f"Học phần {subject} dùng cho dữ liệu mẫu HSMS.",
                )
                db.session.add(course)
            courses.append(course)
        db.session.flush()
        return courses

    @classmethod
    def _student_name(cls, index: int) -> str:
        return (
            f"{cls.FAMILY_NAMES[index % len(cls.FAMILY_NAMES)]} "
            f"{cls.MIDDLE_NAMES[(index // 10) % len(cls.MIDDLE_NAMES)]} "
            f"{cls.FIRST_NAMES[(index // 100 + index) % len(cls.FIRST_NAMES)]}"
        )

    @classmethod
    def _seed_students(cls, classes: list[SchoolClass]) -> list[Student]:
        students: list[Student] = []
        for index in range(1, 501):
            code = f"HSDEMO{index:04d}"
            student = Student.query.filter_by(code=code).first()
            class_index = (index - 1) % len(classes)
            school_class = classes[class_index]
            if not student:
                parent_family = cls.FAMILY_NAMES[(index + 3) % len(cls.FAMILY_NAMES)]
                student = Student(
                    code=code,
                    full_name=cls._student_name(index),
                    gender=index % 2,
                    date_of_birth=date(2008 + (index % 4), 1 + (index % 12), 1 + (index % 27)),
                    address=f"{index} Đường Học Sinh, Phường {1 + index % 20}, Thành phố HSMS",
                    average_score=Decimal(f"{5 + (index % 50) / 10:.1f}"),
                    class_id=school_class.id,
                    household=f"Hộ khẩu số HK{index:04d}, Thành phố HSMS",
                    parent_name=f"{parent_family} Phụ Huynh {index:04d}",
                    parent_phone=f"08{index:08d}",
                    learning_status="Đang học",
                    policy_type=cls.POLICY_TYPES[index % len(cls.POLICY_TYPES)],
                )
                db.session.add(student)
            students.append(student)
        db.session.flush()
        return students

    @classmethod
    def _seed_sections(
        cls,
        classes: list[SchoolClass],
        teachers: list[Teacher],
        courses: list[Course],
    ) -> list[CourseSection]:
        sections: list[CourseSection] = []
        for class_index, school_class in enumerate(classes):
            if not school_class.homeroom_teacher_id:
                school_class.homeroom_teacher_id = teachers[class_index].id
            for course_index, course in enumerate(courses[:6]):
                code = f"HP{school_class.code[-4:]}{course_index + 1:02d}"
                section = CourseSection.query.filter_by(code=code).first()
                if not section:
                    section = CourseSection(
                        code=code,
                        course_id=course.id,
                        class_id=school_class.id,
                        teacher_id=teachers[(class_index * 6 + course_index) % len(teachers)].id,
                        capacity=45,
                        status="open",
                    )
                    db.session.add(section)
                sections.append(section)
        db.session.flush()
        return sections

    @classmethod
    def _seed_schedules(cls, sections: list[CourseSection]) -> int:
        created = 0
        for index, section in enumerate(sections):
            exists = ClassSchedule.query.filter_by(section_id=section.id).first()
            if exists:
                continue
            start_period = 1 + ((index % 4) * 2)
            schedule = ClassSchedule(
                section_id=section.id,
                weekday=cls.WEEKDAYS[index % len(cls.WEEKDAYS)],
                start_period=start_period,
                end_period=start_period + 1,
                room=f"P{100 + index % 35}",
            )
            db.session.add(schedule)
            created += 1
        db.session.flush()
        return ClassSchedule.query.count() if created else ClassSchedule.query.count()

    @classmethod
    def _seed_registrations(cls, students: list[Student], sections: list[CourseSection]) -> int:
        section_map: dict[int, list[CourseSection]] = {}
        for section in sections:
            if section.class_id is not None:
                section_map.setdefault(section.class_id, []).append(section)

        created = 0
        for student in students:
            for section in section_map.get(student.class_id, []):
                exists = CourseRegistration.query.filter_by(section_id=section.id, student_id=student.id).first()
                if exists:
                    continue
                db.session.add(CourseRegistration(section_id=section.id, student_id=student.id, status="active"))
                created += 1
        db.session.flush()
        return CourseRegistration.query.count() if created else CourseRegistration.query.count()

    @classmethod
    def _seed_grades(cls, students: list[Student], sections: list[CourseSection]) -> int:
        section_map: dict[int, list[CourseSection]] = {}
        for section in sections:
            if section.class_id is not None:
                section_map.setdefault(section.class_id, []).append(section)

        created = 0
        for student in students:
            for offset, section in enumerate(section_map.get(student.class_id, [])[:3]):
                exists = GradeRecord.query.filter_by(section_id=section.id, student_id=student.id).first()
                if exists:
                    continue
                base = Decimal("5.0") + Decimal(((student.id or 0) + offset) % 45) / Decimal("10")
                average10 = min(base + Decimal("0.4"), Decimal("10.0"))
                gpa4 = min(Decimal("4.0"), average10 / Decimal("2.5"))
                letter = "A" if average10 >= 8.5 else "B" if average10 >= 7 else "C" if average10 >= 5.5 else "D"
                db.session.add(
                    GradeRecord(
                        section_id=section.id,
                        student_id=student.id,
                        component_score=base,
                        midterm_score=min(base + Decimal("0.3"), Decimal("10.0")),
                        final_score=min(base + Decimal("0.6"), Decimal("10.0")),
                        average10=average10,
                        gpa4=gpa4.quantize(Decimal("0.01")),
                        letter_grade=letter,
                    )
                )
                created += 1
        db.session.flush()
        return GradeRecord.query.count() if created else GradeRecord.query.count()

    @classmethod
    def _seed_finance(cls, students: list[Student]) -> tuple[int, int]:
        invoices_created = 0
        payments_created = 0
        for index, student in enumerate(students, start=1):
            invoice = TuitionInvoice.query.filter_by(student_id=student.id, term="HK1 2026", invoice_type="credit").first()
            if not invoice:
                total = Decimal("350000") * Decimal(6 + (index % 5))
                paid = total if index % 4 else total / Decimal("2")
                status = "paid" if paid >= total else "partial"
                invoice = TuitionInvoice(
                    invoice_code=f"HDDEMO{index:04d}",
                    student_id=student.id,
                    term="HK1 2026",
                    invoice_type="credit",
                    credit_count=6 + (index % 5),
                    unit_price=Decimal("350000"),
                    total_amount=total,
                    paid_amount=paid,
                    status=status,
                    due_date=date.today() + timedelta(days=30 - (index % 40)),
                )
                if invoice.due_date < date.today() and paid < total:
                    invoice.status = "overdue"
                db.session.add(invoice)
                invoices_created += 1
                db.session.flush()

            if invoice.paid_amount and not PaymentRecord.query.filter_by(transaction_ref=f"DEMO-PAY-{index:04d}").first():
                db.session.add(
                    PaymentRecord(
                        payment_code=f"TTDEMO{index:04d}",
                        invoice_id=invoice.id,
                        amount=invoice.paid_amount,
                        method="Chuyển khoản" if index % 3 else "Tiền mặt",
                        transaction_ref=f"DEMO-PAY-{index:04d}",
                        payment_date=date.today() - timedelta(days=index % 20),
                        notes="Thanh toán dữ liệu mẫu.",
                    )
                )
                payments_created += 1
        db.session.flush()
        return TuitionInvoice.query.count() if invoices_created else TuitionInvoice.query.count(), PaymentRecord.query.count() if payments_created else PaymentRecord.query.count()

    @classmethod
    def _seed_admissions(cls, classes: list[SchoolClass]) -> int:
        created = 0
        for index in range(1, 9):
            code = f"TSDEMO{index:03d}"
            if AdmissionApplication.query.filter_by(application_code=code).first():
                continue
            db.session.add(
                AdmissionApplication(
                    application_code=code,
                    full_name=f"{cls.FAMILY_NAMES[index]} {cls.MIDDLE_NAMES[index]} {cls.FIRST_NAMES[index]}",
                    gender=index % 2,
                    date_of_birth=date(2010, 1 + index, 2 + index),
                    address=f"{index} Đường Tuyển Sinh, Thành phố HSMS",
                    phone=f"07{index:08d}",
                    parent_name=f"{cls.FAMILY_NAMES[index]} Phụ Huynh Tuyển Sinh",
                    parent_phone=f"07{index + 100:08d}",
                    admission_score=Decimal("6.0") + Decimal(index) / Decimal("10"),
                    desired_class_id=classes[(index - 1) % len(classes)].id,
                    desired_major="Chương trình phổ thông",
                    status="pending",
                    notes="Hồ sơ mẫu đang chờ xét duyệt.",
                )
            )
            created += 1
        db.session.flush()
        return AdmissionApplication.query.count() if created else AdmissionApplication.query.count()
