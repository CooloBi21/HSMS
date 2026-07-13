from dataclasses import dataclass, field
from typing import Dict, List

from dao import giao_vien_dao, hoc_sinh_dao, lop_dao
from models.activity import ActivityInfo
from services import activity_service


@dataclass
class DashboardStats:
    student_count: int
    class_count: int
    teacher_count: int
    average_score: float
    students_per_class: List[Dict]
    score_per_class: List[Dict]
    academic_distribution: List[Dict]
    notifications: List[Dict] = field(default_factory=list)
    recent_activities: List[ActivityInfo] = field(default_factory=list)
    activity_total: int = 0
    low_score_students: List[str] = field(default_factory=list)
    best_class: str = ""
    worst_class: str = ""


def _classify_score(score: float) -> str:
    if score >= 8.0:
        return "Giỏi"
    if score >= 6.5:
        return "Khá"
    if score >= 5.0:
        return "TB"
    return "Yếu"


def get_recent_activities(page: int = 1, page_size: int = 5) -> List[ActivityInfo]:
    offset = (page - 1) * page_size
    return activity_service.get_recent_activities(limit=page_size, offset=offset)


def get_activity_count() -> int:
    return activity_service.count_activities()


def get_dashboard_stats(activity_page: int = 1, activity_page_size: int = 5) -> DashboardStats:
    students = hoc_sinh_dao.get_all()
    classes = lop_dao.get_all()
    teachers = giao_vien_dao.get_all()

    scores = [s.diem_tb for s in students if s.diem_tb is not None]
    avg = round(sum(scores) / len(scores), 2) if scores else 0.0

    students_per_class = []
    score_per_class = []
    class_avgs: List[tuple] = []

    for lop in classes:
        class_students = [s for s in students if s.ma_lop == lop.ma_lop]
        count = len(class_students)
        students_per_class.append({"label": lop.ten_lop, "value": count})
        if class_students:
            class_avg = sum(s.diem_tb or 0 for s in class_students) / count
            rounded = round(class_avg, 2)
            score_per_class.append({"label": lop.ten_lop, "value": rounded})
            class_avgs.append((lop.ten_lop, rounded))

    academic_counts = {"Giỏi": 0, "Khá": 0, "TB": 0, "Yếu": 0}
    low_score_names: List[str] = []
    for s in students:
        if s.diem_tb is None:
            continue
        academic_counts[_classify_score(s.diem_tb)] += 1
        if s.diem_tb < 5:
            low_score_names.append(s.ho_ten)

    academic_distribution = [{"label": k, "value": v} for k, v in academic_counts.items() if v > 0]
    students_per_class.sort(key=lambda item: item["value"], reverse=True)
    if len(students_per_class) > 6:
        top_classes = students_per_class[:6]
        other_count = sum(item["value"] for item in students_per_class[6:])
        if other_count:
            top_classes.append({"label": "Khac", "value": other_count})
        students_per_class = top_classes
    score_per_class.sort(key=lambda item: item["value"], reverse=True)

    notifications: List[str] = []
    if low_score_names:
        names = ", ".join(low_score_names[:3])
        suffix = f" và {len(low_score_names) - 3} HS khác" if len(low_score_names) > 3 else ""
        notifications.append(f"⚠ {len(low_score_names)} học sinh có điểm TB dưới 5: {names}{suffix}")

    inactive = [t for t in teachers if t.status == "Inactive"]
    if inactive:
        names = ", ".join(f"{t.full_name} ({t.subject or 'chưa có môn'})" for t in inactive[:3])
        suffix = f" và {len(inactive) - 3} người khác" if len(inactive) > 3 else ""
        notifications.append(
            f"⚠ {len(inactive)} giáo viên đang tạm nghỉ / ngừng giảng dạy: {names}{suffix}. "
            "Cần kiểm tra phân công hoặc cập nhật trạng thái."
        )

    empty_classes = [lop.ten_lop for lop in classes if hoc_sinh_dao.count_by_class(lop.ma_lop) == 0]
    if empty_classes:
        notifications.append(f"⚠ Lớp chưa có học sinh: {', '.join(empty_classes)}")

    no_score = [s.ho_ten for s in students if s.diem_tb is None]
    if no_score:
        notifications.append(f"⚠ {len(no_score)} học sinh chưa có điểm TB")

    if class_avgs:
        best = max(class_avgs, key=lambda x: x[1])
        worst = min(class_avgs, key=lambda x: x[1])
        if worst[1] < 7.0:
            notifications.append(f"⚠ Lớp {worst[0]} có điểm TB thấp ({worst[1]}) — cần theo dõi")
    else:
        best = worst = ("—", 0)

    if not notifications:
        notifications.append("✓ Hệ thống hoạt động bình thường — không có cảnh báo khẩn.")

    notification_items = []
    for text in notifications:
        lowered = text.lower()
        if "dÆ°á»›i 5" in lowered or "dưới 5" in lowered or "duoi 5" in lowered:
            level = "critical"
            title = "Hoc sinh co diem TB duoi 5"
        elif "táº¡m nghá»‰" in lowered or "tạm nghỉ" in lowered or "ngá»«ng" in lowered or "ngừng" in lowered or "tháº¥p" in lowered or "thấp" in lowered:
            level = "warning"
            title = "Can kiem tra"
        elif text.startswith("âœ“"):
            level = "success"
            title = "He thong on dinh"
        else:
            level = "info"
            title = "Thong tin"
        notification_items.append({"level": level, "title": title, "detail": text})

    activity_total = get_activity_count()

    return DashboardStats(
        student_count=len(students),
        class_count=len(classes),
        teacher_count=len(teachers),
        average_score=avg,
        students_per_class=students_per_class,
        score_per_class=score_per_class,
        academic_distribution=academic_distribution,
        notifications=notification_items,
        recent_activities=get_recent_activities(activity_page, activity_page_size),
        activity_total=activity_total,
        low_score_students=low_score_names,
        best_class=best[0] if class_avgs else "—",
        worst_class=worst[0] if class_avgs else "—",
    )
