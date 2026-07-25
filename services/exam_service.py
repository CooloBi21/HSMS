from typing import List, Optional

from dao import exam_dao, student_dao, training_dao
from models.exam import ExamEligibilityInfo, ExamScheduleInfo, GradeRecordInfo, GradeReviewInfo
from services import activity_service

EXAM_TYPES = ("Giữa kỳ", "Cuối kỳ", "Thi lại")
ELIGIBILITY_STATUSES = ("Đủ điều kiện", "Bị khóa")
REVIEW_STATUSES = ("Mới", "Đang xử lý", "Đã điều chỉnh", "Từ chối")


def list_exams(section_id: Optional[str] = None) -> List[ExamScheduleInfo]:
    return exam_dao.get_exams(section_id=section_id)


def list_eligibilities(exam_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[ExamEligibilityInfo]:
    return exam_dao.get_eligibilities(exam_id=exam_id, ma_hs=ma_hs)


def list_grades(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[GradeRecordInfo]:
    return exam_dao.get_grades(section_id=section_id, ma_hs=ma_hs)


def list_reviews(status: Optional[str] = None) -> List[GradeReviewInfo]:
    return exam_dao.get_reviews(status=status)


def summary() -> dict:
    eligibilities = list_eligibilities()
    return {
        "exams": len(list_exams()),
        "grades": len(list_grades()),
        "locked": len([e for e in eligibilities if e.status == "Bị khóa"]),
        "reviews": len(list_reviews()),
    }


def next_exam_id() -> str:
    return f"EX{exam_dao.get_max_num('EXAM_SCHEDULE', 'ExamID', 'EX', 2) + 1:04d}"


def next_eligibility_id() -> str:
    return f"DT{exam_dao.get_max_num('EXAM_ELIGIBILITY', 'EligibilityID', 'DT', 2) + 1:05d}"


def next_grade_id() -> str:
    return f"GR{exam_dao.get_max_num('GRADE_RECORD', 'GradeID', 'GR', 2) + 1:05d}"


def next_review_id() -> str:
    return f"PK{exam_dao.get_max_num('GRADE_REVIEW', 'ReviewID', 'PK', 2) + 1:05d}"


def create_exam(exam: ExamScheduleInfo) -> ExamScheduleInfo:
    exam.exam_id = exam.exam_id.strip()
    exam.section_id = exam.section_id.strip()
    exam.exam_date = exam.exam_date.strip()
    exam.shift = exam.shift.strip()
    exam.room = exam.room.strip()
    exam.exam_type = exam.exam_type.strip()
    if not training_dao.get_section(exam.section_id):
        raise ValueError("Lớp học phần không tồn tại.")
    if not exam.exam_date or not exam.shift or not exam.room:
        raise ValueError("Ngày thi, ca thi và phòng thi không được để trống.")
    if exam.exam_type not in EXAM_TYPES:
        raise ValueError("Loại kỳ thi không hợp lệ.")
    if exam_dao.get_exam(exam.exam_id):
        raise ValueError(f"Mã lịch thi '{exam.exam_id}' đã tồn tại.")
    _check_exam_room_conflict(exam)
    exam_dao.insert_exam(exam)
    activity_service.log_activity("Lập lịch thi", f"Lap lịch {exam.exam_type} cho {exam.section_id}")
    return exam


def generate_eligibility_for_exam(exam_id: str, tuition_eligible: bool = True) -> int:
    exam = exam_dao.get_exam(exam_id)
    if not exam:
        raise ValueError("Lịch thi không tồn tại.")
    registrations = training_dao.get_registrations(section_id=exam.section_id)
    for index, reg in enumerate(registrations, start=1):
        attendance_eligible = _attendance_ok(exam.section_id, reg.ma_hs)
        item = ExamEligibilityInfo(
            eligibility_id=f"{exam_id}-{reg.ma_hs}",
            exam_id=exam_id,
            ma_hs=reg.ma_hs,
            candidate_no=f"{index:03d}",
            attendance_eligible=attendance_eligible,
            tuition_eligible=tuition_eligible,
            status="Đủ điều kiện" if attendance_eligible and tuition_eligible else "Bị khóa",
            notes=None if tuition_eligible else "Chỉa Đủ điều kiện học phí.",
        )
        exam_dao.insert_or_update_eligibility(item)
    activity_service.log_activity("Xét điều kiện thi", f"Xet {len(registrations)} học sinh cho lịch thi {exam_id}")
    return len(registrations)


def save_grade(grade: GradeRecordInfo) -> GradeRecordInfo:
    grade.grade_id = grade.grade_id.strip()
    grade.section_id = grade.section_id.strip()
    grade.ma_hs = grade.ma_hs.strip()
    if not training_dao.get_section(grade.section_id):
        raise ValueError("Lớp học phần không tồn tại.")
    if not student_dao.get_by_id(grade.ma_hs):
        raise ValueError("Học sinh không tồn tại.")
    if not any(r.ma_hs == grade.ma_hs for r in training_dao.get_registrations(section_id=grade.section_id)):
        raise ValueError("Học sinh chưa đăng ký học phần này.")
    for score in (grade.component_score, grade.midterm_score, grade.final_score):
        if score is not None and (score < 0 or score > 10):
            raise ValueError("Điểm phải từ 0 đến 10.")
    grade.average10 = calculate_average10(grade)
    grade.gpa4 = calculate_gpa4(grade.average10)
    grade.letter_grade = calculate_letter_grade(grade.average10)
    exam_dao.insert_or_update_grade(grade)
    activity_service.log_activity("Nhập điểm", f"Cập nhật Điểm {grade.ma_hs} - {grade.section_id}")
    return grade


def submit_review(review: GradeReviewInfo) -> GradeReviewInfo:
    review.review_id = review.review_id.strip()
    review.grade_id = review.grade_id.strip()
    review.request_date = review.request_date.strip()
    review.reason = review.reason.strip()
    review.status = review.status or "Mới"
    if not exam_dao.get_grade(review.grade_id):
        raise ValueError("Bảng Điểm cần phúc khảo không tồn tại.")
    if not review.request_date or not review.reason:
        raise ValueError("Ngày yêu cầu và lý do phúc khảo không được để trống.")
    if review.status not in REVIEW_STATUSES:
        raise ValueError("Trạng thái phúc khảo không hợp lệ.")
    if review.adjusted_score is not None and (review.adjusted_score < 0 or review.adjusted_score > 10):
        raise ValueError("Điểm điều chỉnh phải từ 0 đến 10.")
    exam_dao.insert_or_update_review(review)
    if review.status == "Đã điều chỉnh" and review.adjusted_score is not None:
        grade = exam_dao.get_grade(review.grade_id)
        grade.final_score = review.adjusted_score
        save_grade(grade)
    activity_service.log_activity("Phọc khảo", f"Xử lý phúc khảo {review.review_id}")
    return review


def delete_exam(exam_id: str) -> bool:
    return exam_dao.delete_exam(exam_id)


def delete_grade(grade_id: str) -> bool:
    return exam_dao.delete_grade(grade_id)


def delete_eligibility(eligibility_id: str) -> bool:
    return exam_dao.delete_eligibility(eligibility_id)


def delete_review(review_id: str) -> bool:
    return exam_dao.delete_review(review_id)


def calculate_average10(grade: GradeRecordInfo) -> Optional[float]:
    scores = [grade.component_score, grade.midterm_score, grade.final_score]
    if any(score is None for score in scores):
        return None
    return round(grade.component_score * 0.2 + grade.midterm_score * 0.3 + grade.final_score * 0.5, 2)


def calculate_gpa4(average10: Optional[float]) -> Optional[float]:
    if average10 is None:
        return None
    return round(min(4.0, average10 / 10 * 4), 2)


def calculate_letter_grade(average10: Optional[float]) -> Optional[str]:
    if average10 is None:
        return None
    if average10 >= 8.5:
        return "A"
    if average10 >= 7.0:
        return "B"
    if average10 >= 5.5:
        return "C"
    if average10 >= 4.0:
        return "D"
    return "F"


def _attendance_ok(section_id: str, ma_hs: str) -> bool:
    records = training_dao.get_attendance(section_id=section_id, ma_hs=ma_hs)
    total = len(records)
    if total == 0:
        return True
    issues = len([r for r in records if r.status in ("Vắng", "Đi muộn")])
    return issues / total <= 0.2


def _check_exam_room_conflict(exam: ExamScheduleInfo) -> None:
    for existing in exam_dao.get_exams():
        if existing.exam_date == exam.exam_date and existing.shift == exam.shift and existing.room == exam.room:
            raise ValueError("Phòng thi đã được xếp cho ca thi này.")
