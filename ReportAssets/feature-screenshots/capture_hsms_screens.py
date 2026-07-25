from __future__ import annotations

import time
from pathlib import Path
import sys

from PIL import ImageGrab

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dao.db import init_database_if_needed
from services import teacher_service, student_service, school_class_service
from ui.app import HSMSApp


OUT_DIR = Path(__file__).resolve().parent
CAPTIONS = []


def wait(app: HSMSApp, seconds: float = 0.45) -> None:
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
    path = OUT_DIR / filename
    image.save(path)
    CAPTIONS.append((filename, caption))


def set_entry(entry, value: str) -> None:
    entry.configure(state="normal")
    entry.delete(0, "end")
    entry.insert(0, value)


def main() -> None:
    init_database_if_needed()
    app = HSMSApp()
    app.geometry("1360x760+40+20")
    app.minsize(1200, 720)
    wait(app, 0.8)

    # Dashboard
    app._show_view("dashboard")
    screenshot(
        app,
        "01_dashboard_overview.png",
        "Hình 1. Dashboard điều hành sau redesign: KPI tổng quan, biểu đồ phân tích, cảnh báo và hoạt động gần đây.",
    )

    # Students
    app._show_view("students")
    students_view = app._views["students"]
    screenshot(
        app,
        "02_students_overview.png",
        "Hình 2. Màn Quản lý Học sinh: KPI, form hồ sơ, toolbar tìm kiếm/lọc và bảng danh sách học sinh.",
    )

    students_view._on_new_clicked()
    screenshot(
        app,
        "03_students_add_new_autocode.png",
        "Hình 3. Thao tác bấm '+ Thêm học sinh': mã học sinh được tự sinh và form sẵn sàng nhập dữ liệu mới.",
    )

    students = student_service.list_students()
    if students:
        students_view._fill_form(students[0])
        screenshot(
            app,
            "04_students_select_edit.png",
            "Hình 4. Thao tác chọn một học sinh trong bảng: dữ liệu được nạp lên form để cập nhật.",
        )

    set_entry(students_view._search, "Nguyễn")
    students_view._on_filter_change()
    screenshot(
        app,
        "05_students_search_filter.png",
        "Hình 5. Tìm kiếm học sinh theo từ khóa: bảng chỉ hiển thị các bản ghi phù hợp.",
    )
    set_entry(students_view._search, "")
    students_view._on_filter_change()

    # Classes
    app._show_view("classes")
    classes_view = app._views["classes"]
    screenshot(
        app,
        "06_classes_overview.png",
        "Hình 6. Màn Quản lý Lớp học: KPI lớp, form thông tin lớp, bộ lọc khối và bảng trạng thái lớp.",
    )

    classes_view._on_new_clicked()
    screenshot(
        app,
        "07_classes_add_new_autocode.png",
        "Hình 7. Thao tác bấm '+ Thêm lớp': mã lớp được tự sinh, dropdown khối có placeholder rõ ràng.",
    )

    classes_view._filter_khoi.set("Khối 10")
    classes_view._on_filter_change()
    screenshot(
        app,
        "08_classes_filter_grade.png",
        "Hình 8. Lọc danh sách lớp theo khối 10: bảng lớp học được thu gọn theo bộ lọc.",
    )
    classes_view._filter_khoi.set("Tất cả khối")
    classes_view._on_filter_change()

    classes = school_class_service.list_classes()
    if classes:
        classes_view._fill_form(classes[0])
        screenshot(
            app,
            "09_classes_select_edit.png",
            "Hình 9. Thao tác chọn một lớp: thông tin lớp được đưa lên form để sửa.",
        )

    # Teachers
    app._show_view("teachers")
    teachers_view = app._views["teachers"]
    screenshot(
        app,
        "10_teachers_overview.png",
        "Hình 10. Màn Quản lý Giáo viên: KPI, form hồ sơ, lọc môn/trạng thái và bảng giáo viên.",
    )

    teachers_view._on_new_clicked()
    screenshot(
        app,
        "11_teachers_add_new_autocode.png",
        "Hình 11. Thao tác bấm '+ Thêm giáo viên': mã giáo viên được tự sinh và các dropdown đã có placeholder.",
    )

    teachers_view._status_filter.set("Tạm nghỉ")
    teachers_view._on_filter_change()
    screenshot(
        app,
        "12_teachers_filter_status.png",
        "Hình 12. Lọc giáo viên theo trạng thái Tạm nghỉ: hệ thống hiển thị đúng giáo viên cần theo dõi.",
    )
    teachers_view._status_filter.set("Tất cả trạng thái")
    teachers_view._on_filter_change()

    teachers = teacher_service.list_teachers()
    if teachers:
        teachers_view._fill_form(teachers[0])
        screenshot(
            app,
            "13_teachers_select_edit.png",
            "Hình 13. Thao tác chọn một giáo viên: dữ liệu được nạp lên form để cập nhật hồ sơ.",
        )

    app._theme_btn.invoke()
    wait(app, 0.6)
    screenshot(
        app,
        "14_dark_mode_dashboard.png",
        "Hình 14. Kiểm tra chế độ tối: dashboard vẫn giữ tương phản, card, bảng và biểu đồ đọc được.",
    )

    caption_path = OUT_DIR / "HSMS_feature_screenshot_captions.md"
    lines = ["# HSMS Feature Screenshot Captions", ""]
    for filename, caption in CAPTIONS:
        lines.append(f"- `{filename}` - {caption}")
    caption_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    app.destroy()


if __name__ == "__main__":
    main()
