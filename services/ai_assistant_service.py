import re
from typing import Optional

from dao import teacher_dao, student_dao, school_class_dao
from utils.labels import teacher_status_vi


def answer_question(question: str) -> str:
    q = question.strip().lower()
    if not q:
        return "Vui lòng nhập câu hỏi.\n\nVí dụ:\n• Học sinh nào có điểm dưới 5?\n• Lớp nào học tốt nhất?\n• Giáo viên nào đang tạm nghỉ?"

    if _match(q, ["inactive", "tạm nghỉ", "ngừng giảng", "nghỉ dạy", "không dạy"]):
        return _answer_inactive_teachers()

    if _match(q, ["điểm dưới", "điểm thấp", "yếu", "dưới 5"]):
        return _answer_low_score_students()

    if _match(q, ["lớp nào", "học tốt", "tốt nhất", "điểm cao"]):
        return _answer_best_class()

    if _match(q, ["bao nhiêu học sinh", "tổng học sinh", "số học sinh"]):
        students = student_dao.get_all()
        return f"Hiện có {len(students)} học sinh trong hệ thống."

    if _match(q, ["bao nhiêu giáo viên", "tổng giáo viên"]):
        teachers = teacher_dao.get_all()
        active = sum(1 for t in teachers if t.status == "Active")
        inactive = len(teachers) - active
        return (
            f"Hiện có {len(teachers)} giáo viên.\n"
            f"• Đang giảng dạy: {active}\n"
            f"• Tạm nghỉ / ngừng giảng dạy: {inactive}"
        )

    return (
        "Tôi chưa hiểu câu hỏi này.\n\n"
        "Bạn có thể hỏi:\n"
        "• Giáo viên nào đang tạm nghỉ?\n"
        "• Học sinh nào có điểm dưới 5?\n"
        "• Lớp nào học tốt nhất?\n"
        "• Có bao nhiêu học sinh / giáo viên?"
    )


def _match(q: str, keywords: list) -> bool:
    return any(k in q for k in keywords)


def _answer_inactive_teachers() -> str:
    teachers = [t for t in teacher_dao.get_all() if t.status == "Inactive"]
    if not teachers:
        return "Hiện không có giáo viên nào ở trạng thái tạm nghỉ / ngừng giảng dạy."

    lines = [
        f"Có {len(teachers)} giáo viên đang tạm nghỉ / ngừng giảng dạy "
        "(không còn phụ trách lớp trong hệ thống):\n"
    ]
    for t in teachers:
        lines.append(f"• {t.full_name} — môn {t.subject or 'chưa xác định'} (mã {t.teacher_code})")
    lines.append("\nGợi ý: vào mục Giáo viên để cập nhật trạng thái hoặc phân công lại.")
    return "\n".join(lines)


def _answer_low_score_students() -> str:
    students = [s for s in student_dao.get_all() if s.diem_tb is not None and s.diem_tb < 5]
    if not students:
        return "Không có học sinh nào có điểm trung bình dưới 5."

    lines = [f"Có {len(students)} học sinh có điểm TB dưới 5:\n"]
    for s in students:
        lines.append(f"• {s.ho_ten} — điểm {s.diem_tb} (lớp {s.ma_lop or '—'})")
    return "\n".join(lines)


def _answer_best_class() -> str:
    classes = school_class_dao.get_all()
    students = student_dao.get_all()
    best_name = ""
    best_avg = -1.0

    for lop in classes:
        class_students = [s for s in students if s.ma_lop == lop.ma_lop and s.diem_tb is not None]
        if not class_students:
            continue
        avg = sum(s.diem_tb for s in class_students) / len(class_students)
        if avg > best_avg:
            best_avg = avg
            best_name = lop.ten_lop

    if not best_name:
        return "Chưa đủ dữ liệu điểm để xếp hạng lớp."

    return f"Lớp có điểm trung bình cao nhất hiện tại là {best_name} với điểm TB {best_avg:.2f}."
