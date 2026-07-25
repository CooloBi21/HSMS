from __future__ import annotations

import sys
import time
from pathlib import Path

from PIL import ImageGrab

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dao.db import init_database_if_needed
from models.admission import AdmissionApplicationInfo
from models.exam import ExamScheduleInfo, GradeRecordInfo, GradeReviewInfo
from models.finance import PaymentRecordInfo, TuitionInvoiceInfo
from models.graduation import (
    AlumniEmploymentInfo,
    DiplomaRecordInfo,
    DocumentRequestInfo,
    GraduationCheckInfo,
)
from models.student_affairs import (
    ConductScoreInfo,
    DormAssignmentInfo,
    ExtracurricularActivityInfo,
    HealthRecordInfo,
)
from models.student_decision import StudentDecisionInfo
from models.training import (
    AttendanceRecordInfo,
    ClassScheduleInfo,
    CourseInfo,
    CourseRegistrationInfo,
    CourseSectionInfo,
    CurriculumItemInfo,
)
from services import (
    admission_service,
    exam_service,
    finance_service,
    graduation_service,
    school_class_service,
    student_affairs_service,
    student_decision_service,
    student_service,
    teacher_service,
    training_service,
)
from ui.app import HSMSApp


OUT_DIR = Path(__file__).resolve().parent
CAPTIONS: list[tuple[str, str]] = []
TODAY = "2026-07-22"


def wait(app: HSMSApp, seconds: float = 0.35) -> None:
    app.deiconify()
    app.lift()
    app.focus_force()
    app.attributes("-topmost", True)
    app.update_idletasks()
    app.update()
    time.sleep(seconds)
    app.update_idletasks()
    app.update()


def screenshot(app: HSMSApp, filename: str, caption: str) -> None:
    wait(app)
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    image = ImageGrab.grab((x, y, x + w, y + h))
    app.attributes("-topmost", False)
    path = OUT_DIR / filename
    image.save(path)
    CAPTIONS.append((filename, caption))


def set_entry(entry, value: str) -> None:
    try:
        entry.configure(state="normal")
    except Exception:
        pass
    entry.delete(0, "end")
    entry.insert(0, value)


def select_tab(view, label: str) -> None:
    for child in view.winfo_children():
        if child.__class__.__name__ == "CTkTabview":
            child.set(label)
            return
    raise RuntimeError(f"Cannot find tabview for {view}")


def first_label(mapping: dict, code: str) -> str:
    for label, value in mapping.items():
        if value == code:
            return label
    return next(iter(mapping.keys()))


def show_admissions(app: HSMSApp, application_id: str) -> None:
    view = app._views["admissions"]
    app._show_view("admissions")
    set_entry(view._search, application_id)
    view._status_filter.set(view._status_filter.cget("values")[0])
    view.refresh()
    record = admission_service.get_application(application_id)
    if record:
        view._fill_form(record)


def show_profiles(app: HSMSApp, student_code: str, decision_id: str | None = None) -> None:
    view = app._views["profiles"]
    app._show_view("profiles")
    view.refresh()
    label = first_label(view._student_map, student_code)
    view._student_combo.set(label)
    view._decision_student.set(label)
    if decision_id:
        set_entry(view._decision_search, decision_id)
    view.refresh()


def show_training(app: HSMSApp, tab: str) -> None:
    view = app._views["training"]
    app._show_view("training")
    select_tab(view, tab)
    view.refresh()


def show_exams(app: HSMSApp, tab: str) -> None:
    view = app._views["exams"]
    app._show_view("exams")
    select_tab(view, tab)
    view.refresh()


def show_finance(app: HSMSApp, tab: str) -> None:
    view = app._views["finance"]
    app._show_view("finance")
    select_tab(view, tab)
    view.refresh()


def show_affairs(app: HSMSApp, tab: str) -> None:
    view = app._views["affairs"]
    app._show_view("affairs")
    select_tab(view, tab)
    view.refresh()


def show_graduation(app: HSMSApp, tab: str) -> None:
    view = app._views["graduation"]
    app._show_view("graduation")
    select_tab(view, tab)
    view.refresh()


def create_test_data() -> dict:
    classes = school_class_service.list_classes()
    teachers = teacher_service.list_teachers()
    students = student_service.list_students()
    if not classes or not teachers or not students:
        raise RuntimeError("Need at least one class, teacher, and student before running BTTH06 tests.")

    class_code = classes[0].ma_lop
    teacher_id = teachers[0].teacher_id
    primary_student = students[0].ma_hs

    app_id = admission_service.generate_next_id()
    admission = AdmissionApplicationInfo(
        application_id=app_id,
        full_name="BTTH06 Test Tuyen Sinh",
        gender=1,
        dob="2009-09-09",
        address="Dia chi test BTTH06",
        phone="0906000001",
        parent_name="Phu huynh BTTH06",
        parent_phone="0906000002",
        admission_score=8.4,
        desired_class=class_code,
        desired_major="Khoa hoc tu nhien",
        status=admission_service.APPLICATION_STATUSES[0],
        notes="Test tiep nhan ho so BTTH06",
    )
    admission_service.create_application(admission)
    admission_service.auto_screen_application(app_id, pass_score=5.0)
    enrolled_student = admission_service.enroll_application(app_id, class_code).ma_hs

    student = student_service.get_student(enrolled_student)
    student.ho_khau = "TP. Ho Chi Minh"
    student.parent_name = "Phu huynh BTTH06"
    student.parent_phone = "0906000002"
    student.learning_status = student_service.LEARNING_STATUSES[0]
    student.policy_type = student_service.POLICY_TYPES[1]
    student_service.update_student_profile(student)

    decision_id = student_decision_service.generate_next_id()
    student_decision_service.create_decision(
        StudentDecisionInfo(
            decision_id=decision_id,
            ma_hs=enrolled_student,
            decision_type=student_decision_service.DECISION_TYPES[0],
            decision_date=TODAY,
            title="Khen thuong BTTH06",
            description="Minh chung quan ly khen thuong/ky luat",
            issuer="Admin HSMS",
        )
    )

    course_id = training_service.next_course_id()
    training_service.create_course(
        CourseInfo(course_id, "BTTH06 Mon Tich Hop", 3, "10", None, "Mon hoc dung cho test tong hop")
    )
    curriculum_id = training_service.next_curriculum_id()
    training_service.create_curriculum_item(
        CurriculumItemInfo(curriculum_id, course_id, "10", "HK1 2026", 1, "Test khung chuong trinh")
    )
    section_id = training_service.next_section_id()
    training_service.create_section(
        CourseSectionInfo(section_id, course_id, class_code, teacher_id, 60, training_service.SECTION_STATUSES[0])
    )
    registration_id = training_service.next_registration_id()
    training_service.register_student(
        CourseRegistrationInfo(registration_id, section_id, primary_student, training_service.REGISTRATION_STATUSES[0])
    )
    schedule_id = training_service.next_schedule_id()
    schedule = None
    for day in training_service.WEEKDAYS:
        for start_period in range(1, 13, 2):
            candidate = ClassScheduleInfo(
                schedule_id,
                section_id,
                day,
                start_period,
                start_period + 1,
                f"BTTH06-{section_id}-{start_period}",
            )
            try:
                schedule = training_service.create_schedule(candidate)
                break
            except ValueError as exc:
                if "trùng" not in str(exc).lower() and "trung" not in str(exc).lower():
                    raise
        if schedule:
            break
    if not schedule:
        raise RuntimeError("Cannot find a free BTTH06 schedule slot.")
    attendance_id = training_service.next_attendance_id()
    training_service.record_attendance(
        AttendanceRecordInfo(
            attendance_id,
            section_id,
            primary_student,
            TODAY,
            training_service.ATTENDANCE_STATUSES[1],
            "Test chuyen can BTTH06",
        )
    )

    exam_id = exam_service.next_exam_id()
    exam_service.create_exam(
        ExamScheduleInfo(exam_id, section_id, "2026-08-01", "Ca 1", f"BTTH06-{exam_id}", exam_service.EXAM_TYPES[1])
    )
    exam_service.generate_eligibility_for_exam(exam_id, tuition_eligible=True)
    grade_id = exam_service.next_grade_id()
    exam_service.save_grade(
        GradeRecordInfo(grade_id, section_id, primary_student, 8.0, 8.5, 9.0)
    )
    review_id = exam_service.next_review_id()
    exam_service.submit_review(
        GradeReviewInfo(
            review_id,
            grade_id,
            TODAY,
            "Test phuc khao BTTH06",
            exam_service.REVIEW_STATUSES[2],
            9.2,
            "Da dieu chinh sau phuc khao",
        )
    )

    invoice_id = finance_service.next_invoice_id()
    finance_service.create_invoice(
        TuitionInvoiceInfo(
            invoice_id,
            primary_student,
            "BTTH06 HK1 2026",
            finance_service.INVOICE_TYPES[0],
            credit_count=3,
            unit_price=350000,
            fixed_amount=0,
            due_date="2026-08-15",
        )
    )
    payment_id = finance_service.next_payment_id()
    finance_service.record_payment(
        PaymentRecordInfo(payment_id, invoice_id, TODAY, 500000, finance_service.PAYMENT_METHODS[1], "BTTH06-PAY")
    )
    finance_service.scan_scholarships("BTTH06 HK1 2026", min_gpa4=3.6, amount=1000000, conduct_score=90)

    conduct_id = student_affairs_service.next_conduct_id()
    student_affairs_service.save_conduct_score(
        ConductScoreInfo(conduct_id, primary_student, "BTTH06 HK1 2026", 92, 88, 95)
    )
    dorm_id = student_affairs_service.next_dorm_id()
    student_affairs_service.save_dorm_assignment(
        DormAssignmentInfo(
            dorm_id,
            enrolled_student,
            "BTTH06-A",
            "601",
            "B1",
            TODAY,
            None,
            120000,
            student_affairs_service.DORM_STATUSES[0],
            "Test KTX BTTH06",
        )
    )
    activity_id = student_affairs_service.next_activity_id()
    student_affairs_service.save_activity(
        ExtracurricularActivityInfo(
            activity_id,
            primary_student,
            "Chien dich tinh nguyen BTTH06",
            "Tinh nguyen",
            TODAY,
            "Thanh vien",
            12,
            student_affairs_service.ACTIVITY_STATUSES[1],
            "Test ngoai khoa BTTH06",
        )
    )
    health_id = student_affairs_service.next_health_id()
    student_affairs_service.save_health_record(
        HealthRecordInfo(
            health_id,
            primary_student,
            TODAY,
            168,
            58,
            student_affairs_service.HEALTH_STATUSES[0],
            "BHYT-BTTH06",
            "2027-07-22",
            "Test y te BTTH06",
        )
    )

    check_id = graduation_service.next_check_id()
    graduation_service.check_graduation(
        GraduationCheckInfo(check_id, primary_student, TODAY, 3, -1, True, True, True)
    )
    diploma_id = graduation_service.next_diploma_id()
    graduation_service.save_diploma(
        DiplomaRecordInfo(
            diploma_id,
            primary_student,
            "SG-BTTH06",
            "VB-BTTH06",
            TODAY,
            graduation_service.DIPLOMA_STATUSES[0],
            check_id,
        )
    )
    document_id = graduation_service.next_document_id()
    graduation_service.save_document_request(
        DocumentRequestInfo(
            document_id,
            primary_student,
            graduation_service.DOCUMENT_TYPES[0],
            TODAY,
            graduation_service.DOCUMENT_STATUSES[2],
        )
    )
    alumni_id = graduation_service.next_alumni_id()
    graduation_service.save_alumni(
        AlumniEmploymentInfo(
            alumni_id,
            primary_student,
            TODAY,
            graduation_service.EMPLOYMENT_STATUSES[0],
            "Cong ty BTTH06",
            "Thuc tap sinh",
            7000000,
            "Test viec lam cuu sinh vien",
        )
    )

    return {
        "application_id": app_id,
        "enrolled_student": enrolled_student,
        "primary_student": primary_student,
        "decision_id": decision_id,
        "course_id": course_id,
        "section_id": section_id,
        "attendance_id": attendance_id,
        "exam_id": exam_id,
        "grade_id": grade_id,
        "review_id": review_id,
        "invoice_id": invoice_id,
        "payment_id": payment_id,
        "conduct_id": conduct_id,
        "dorm_id": dorm_id,
        "activity_id": activity_id,
        "health_id": health_id,
        "check_id": check_id,
        "diploma_id": diploma_id,
        "document_id": document_id,
        "alumni_id": alumni_id,
    }


def run_test_flow(app: HSMSApp) -> None:
    classes = school_class_service.list_classes()
    teachers = teacher_service.list_teachers()
    students = student_service.list_students()
    if not classes or not teachers or not students:
        raise RuntimeError("Need at least one class, teacher, and student before running BTTH06 tests.")

    class_code = classes[0].ma_lop
    teacher_id = teachers[0].teacher_id
    primary_student = students[0].ma_hs

    app_id = admission_service.generate_next_id()
    admission_service.create_application(
        AdmissionApplicationInfo(
            application_id=app_id,
            full_name="BTTH06 Test Tuyen Sinh",
            gender=1,
            dob="2009-09-09",
            address="Dia chi test BTTH06",
            phone="0906000001",
            parent_name="Phu huynh BTTH06",
            parent_phone="0906000002",
            admission_score=8.4,
            desired_class=class_code,
            desired_major="Khoa hoc tu nhien",
            status=admission_service.APPLICATION_STATUSES[0],
            notes="Test tiep nhan ho so BTTH06",
        )
    )
    show_admissions(app, app_id)
    screenshot(app, "BTTH06_TC01_admission_application_received.png", "Hinh 1. Tiep nhan ho so tuyen sinh BTTH06: form va bang hien thi ho so moi da duoc ghi nhan.")

    admission_service.auto_screen_application(app_id, pass_score=5.0)
    show_admissions(app, app_id)
    screenshot(app, "BTTH06_TC02_admission_auto_screen_passed.png", "Hinh 2. Xet tuyen tu dong: ho so BTTH06 dat diem chuan va chuyen sang trang thai dat.")

    enrolled_student = admission_service.enroll_application(app_id, class_code).ma_hs
    show_admissions(app, app_id)
    screenshot(app, "BTTH06_TC03_admission_enrolled_student_code.png", "Hinh 3. Nhap hoc va cap ma hoc sinh: ho so tuyen sinh da co ma hoc sinh moi va lop du kien.")

    student = student_service.get_student(enrolled_student)
    student.ho_khau = "TP. Ho Chi Minh"
    student.parent_name = "Phu huynh BTTH06"
    student.parent_phone = "0906000002"
    student.learning_status = student_service.LEARNING_STATUSES[0]
    student.policy_type = student_service.POLICY_TYPES[1]
    student_service.update_student_profile(student)
    show_profiles(app, enrolled_student)
    screenshot(app, "BTTH06_TC04_profile_status_policy_update.png", "Hinh 4. Cap nhat ly lich hoc sinh: trang thai hoc tap, thong tin phu huynh va dien chinh sach duoc quan ly trong Ho so.")

    decision_id = student_decision_service.generate_next_id()
    student_decision_service.create_decision(
        StudentDecisionInfo(
            decision_id=decision_id,
            ma_hs=enrolled_student,
            decision_type=student_decision_service.DECISION_TYPES[0],
            decision_date=TODAY,
            title="Khen thuong BTTH06",
            description="Minh chung quan ly khen thuong/ky luat",
            issuer="Admin HSMS",
        )
    )
    show_profiles(app, enrolled_student, decision_id)
    screenshot(app, "BTTH06_TC05_profile_reward_decision.png", "Hinh 5. Quan ly khen thuong/ky luat: quyet dinh khen thuong BTTH06 duoc gan cho hoc sinh.")

    course_id = training_service.next_course_id()
    training_service.create_course(
        CourseInfo(course_id, "BTTH06 Mon Tich Hop", 3, "10", None, "Mon hoc dung cho test tong hop")
    )
    curriculum_id = training_service.next_curriculum_id()
    training_service.create_curriculum_item(
        CurriculumItemInfo(curriculum_id, course_id, "10", "HK1 2026", 1, "Test khung chuong trinh")
    )
    show_training(app, "Khung CT")
    screenshot(app, "BTTH06_TC06_training_curriculum_course.png", "Hinh 6. Quan ly khung chuong trinh: mon hoc va dong khung chuong trinh BTTH06 duoc tao.")

    section_id = training_service.next_section_id()
    training_service.create_section(
        CourseSectionInfo(section_id, course_id, class_code, teacher_id, 60, training_service.SECTION_STATUSES[0])
    )
    registration_id = training_service.next_registration_id()
    training_service.register_student(
        CourseRegistrationInfo(registration_id, section_id, primary_student, training_service.REGISTRATION_STATUSES[0])
    )
    show_training(app, "Học phần")
    screenshot(app, "BTTH06_TC07_training_section_registration.png", "Hinh 7. Dang ky hoc phan: lop hoc phan BTTH06 co hoc sinh dang ky va si so duoc cap nhat.")

    schedule_id = training_service.next_schedule_id()
    schedule = None
    for day in training_service.WEEKDAYS:
        for start_period in range(1, 13, 2):
            candidate = ClassScheduleInfo(
                schedule_id,
                section_id,
                day,
                start_period,
                start_period + 1,
                f"BTTH06-{section_id}-{start_period}",
            )
            try:
                schedule = training_service.create_schedule(candidate)
                break
            except ValueError as exc:
                if "trùng" not in str(exc).lower() and "trung" not in str(exc).lower():
                    raise
        if schedule:
            break
    if not schedule:
        raise RuntimeError("Cannot find a free BTTH06 schedule slot.")
    show_training(app, "TKB")
    screenshot(app, "BTTH06_TC08_training_schedule.png", "Hinh 8. Xep thoi khoa bieu: lich hoc BTTH06 gan hoc phan, thu, tiet va phong hoc.")

    attendance_id = training_service.next_attendance_id()
    training_service.record_attendance(
        AttendanceRecordInfo(
            attendance_id,
            section_id,
            primary_student,
            TODAY,
            training_service.ATTENDANCE_STATUSES[1],
            "Test chuyen can BTTH06",
        )
    )
    show_training(app, "Điểm danh")
    screenshot(app, "BTTH06_TC09_training_attendance.png", "Hinh 9. Diem danh va chuyen can: ban ghi vang/di muon duoc luu theo hoc sinh va hoc phan.")

    exam_id = exam_service.next_exam_id()
    exam_service.create_exam(
        ExamScheduleInfo(exam_id, section_id, "2026-08-01", "Ca 1", f"BTTH06-{exam_id}", exam_service.EXAM_TYPES[1])
    )
    exam_service.generate_eligibility_for_exam(exam_id, tuition_eligible=True)
    show_exams(app, "Lịch thi")
    screenshot(app, "BTTH06_TC10_exam_schedule_eligibility.png", "Hinh 10. Lap lich thi va xet dieu kien: lich thi BTTH06 tao danh sach so bao danh/du dieu kien.")

    grade_id = exam_service.next_grade_id()
    exam_service.save_grade(GradeRecordInfo(grade_id, section_id, primary_student, 8.0, 8.5, 9.0))
    show_exams(app, "Điểm")
    screenshot(app, "BTTH06_TC11_exam_grade_gpa.png", "Hinh 11. Nhap diem va tinh GPA: diem thanh phan, giua ky, cuoi ky duoc quy doi TB10/GPA4.")

    review_id = exam_service.next_review_id()
    exam_service.submit_review(
        GradeReviewInfo(
            review_id,
            grade_id,
            TODAY,
            "Test phuc khao BTTH06",
            exam_service.REVIEW_STATUSES[2],
            9.2,
            "Da dieu chinh sau phuc khao",
        )
    )
    show_exams(app, "Phúc khảo")
    screenshot(app, "BTTH06_TC12_exam_grade_review.png", "Hinh 12. Quan ly phuc khao: yeu cau phuc khao BTTH06 da dieu chinh diem va luu trang thai xu ly.")

    invoice_id = finance_service.next_invoice_id()
    finance_service.create_invoice(
        TuitionInvoiceInfo(
            invoice_id,
            primary_student,
            "BTTH06 HK1 2026",
            finance_service.INVOICE_TYPES[0],
            credit_count=3,
            unit_price=350000,
            fixed_amount=0,
            due_date="2026-08-15",
        )
    )
    show_finance(app, "Học phí")
    screenshot(app, "BTTH06_TC13_finance_invoice.png", "Hinh 13. Tinh hoc phi: hoa don BTTH06 tinh theo tin chi va ghi tong phai thu.")

    payment_id = finance_service.next_payment_id()
    finance_service.record_payment(
        PaymentRecordInfo(payment_id, invoice_id, TODAY, 500000, finance_service.PAYMENT_METHODS[1], "BTTH06-PAY")
    )
    show_finance(app, "Thanh toán")
    screenshot(app, "BTTH06_TC14_finance_payment_debt.png", "Hinh 14. Thu phi va cong no: thanh toan mot phan duoc ghi nhan, bang cong no hien so tien con lai.")

    finance_service.scan_scholarships("BTTH06 HK1 2026", min_gpa4=3.6, amount=1000000, conduct_score=90)
    show_finance(app, "Học bổng")
    screenshot(app, "BTTH06_TC15_finance_scholarship_scan.png", "Hinh 15. Xet hoc bong: he thong quet diem/GPA va tao danh sach de xuat hoc bong.")

    conduct_id = student_affairs_service.next_conduct_id()
    student_affairs_service.save_conduct_score(
        ConductScoreInfo(conduct_id, primary_student, "BTTH06 HK1 2026", 92, 88, 95)
    )
    show_affairs(app, "Rèn luyện")
    screenshot(app, "BTTH06_TC16_affairs_conduct_score.png", "Hinh 16. Danh gia diem ren luyen: diem thanh phan duoc tong hop thanh tong diem va xep loai.")

    dorm_id = student_affairs_service.next_dorm_id()
    student_affairs_service.save_dorm_assignment(
        DormAssignmentInfo(
            dorm_id,
            enrolled_student,
            "BTTH06-A",
            "601",
            "B1",
            TODAY,
            None,
            120000,
            student_affairs_service.DORM_STATUSES[0],
            "Test KTX BTTH06",
        )
    )
    show_affairs(app, "KTX")
    screenshot(app, "BTTH06_TC17_affairs_dorm_assignment.png", "Hinh 17. Quan ly ky tuc xa: hoc sinh duoc sap phong, giuong va phi dien nuoc.")

    activity_id = student_affairs_service.next_activity_id()
    student_affairs_service.save_activity(
        ExtracurricularActivityInfo(
            activity_id,
            primary_student,
            "Chien dich tinh nguyen BTTH06",
            "Tinh nguyen",
            TODAY,
            "Thanh vien",
            12,
            student_affairs_service.ACTIVITY_STATUSES[1],
            "Test ngoai khoa BTTH06",
        )
    )
    show_affairs(app, "Ngoại khóa")
    screenshot(app, "BTTH06_TC18_affairs_extracurricular.png", "Hinh 18. Theo doi ngoai khoa: hoat dong, vai tro, so gio va trang thai tham gia duoc ghi nhan.")

    health_id = student_affairs_service.next_health_id()
    student_affairs_service.save_health_record(
        HealthRecordInfo(
            health_id,
            primary_student,
            TODAY,
            168,
            58,
            student_affairs_service.HEALTH_STATUSES[0],
            "BHYT-BTTH06",
            "2027-07-22",
            "Test y te BTTH06",
        )
    )
    show_affairs(app, "Y tế")
    screenshot(app, "BTTH06_TC19_affairs_health_record.png", "Hinh 19. Quan ly y te hoc duong: lich su kham suc khoe va thong tin BHYT duoc luu.")

    check_id = graduation_service.next_check_id()
    graduation_service.check_graduation(
        GraduationCheckInfo(check_id, primary_student, TODAY, 3, -1, True, True, True)
    )
    show_graduation(app, "Xet TN")
    screenshot(app, "BTTH06_TC20_graduation_check.png", "Hinh 20. Xet dieu kien tot nghiep: tin chi, chung chi dau ra va trang thai dat/chua dat duoc kiem tra.")

    diploma_id = graduation_service.next_diploma_id()
    graduation_service.save_diploma(
        DiplomaRecordInfo(
            diploma_id,
            primary_student,
            "SG-BTTH06",
            "VB-BTTH06",
            TODAY,
            graduation_service.DIPLOMA_STATUSES[0],
            check_id,
        )
    )
    show_graduation(app, "Văn bằng")
    screenshot(app, "BTTH06_TC21_graduation_diploma.png", "Hinh 21. Cap phat van bang: so goc, so bang, ngay cap va trang thai van bang duoc quan ly.")

    document_id = graduation_service.next_document_id()
    graduation_service.save_document_request(
        DocumentRequestInfo(
            document_id,
            primary_student,
            graduation_service.DOCUMENT_TYPES[0],
            TODAY,
            graduation_service.DOCUMENT_STATUSES[2],
        )
    )
    show_graduation(app, "Biểu mẫu")
    screenshot(app, "BTTH06_TC22_graduation_document_emis.png", "Hinh 22. Xuat bang diem/giay chung nhan va thong ke EMIS: yeu cau bieu mau duoc tao kem duong dan.")

    alumni_id = graduation_service.next_alumni_id()
    graduation_service.save_alumni(
        AlumniEmploymentInfo(
            alumni_id,
            primary_student,
            TODAY,
            graduation_service.EMPLOYMENT_STATUSES[0],
            "Cong ty BTTH06",
            "Thuc tap sinh",
            7000000,
            "Test viec lam cuu sinh vien",
        )
    )
    show_graduation(app, "Cựu SV")
    screenshot(app, "BTTH06_TC23_graduation_alumni_employment.png", "Hinh 23. Quan ly viec lam cuu sinh vien: khao sat viec lam, cong ty, vi tri va thu nhap duoc luu.")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    init_database_if_needed()

    app = HSMSApp()
    app.geometry("1500x900+30+20")
    app.minsize(1280, 760)
    wait(app, 0.8)

    run_test_flow(app)

    lines = ["# BTTH06 Test Case Captions", ""]
    for filename, caption in CAPTIONS:
        lines.append(f"- `{filename}` - {caption}")
    (OUT_DIR / "BTTH06_test_case_captions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    app.destroy()
    print(f"Captured {len(CAPTIONS)} screenshots in {OUT_DIR}")


if __name__ == "__main__":
    main()
