from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ReportAssets" / "feature-screenshots"

BG = "#f4f7fb"
INK = "#172033"
MUTED = "#5d6b82"
CARD = "#ffffff"
BORDER = "#dbe4f0"
BLUE = "#2563eb"
GREEN = "#059669"
AMBER = "#d97706"
PURPLE = "#7c3aed"
RED = "#dc2626"


def font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


FONT_UI = font("C:/Windows/Fonts/segoeui.ttf", 30)
FONT_UI_BOLD = font("C:/Windows/Fonts/segoeuib.ttf", 34)
FONT_UI_SMALL = font("C:/Windows/Fonts/segoeui.ttf", 23)
FONT_MONO = font("C:/Windows/Fonts/consola.ttf", 22)
FONT_MONO_SMALL = font("C:/Windows/Fonts/consola.ttf", 19)


def read_lines(relative: str) -> list[str]:
    return (ROOT / relative).read_text(encoding="utf-8").splitlines()


def extract_block(relative: str, marker: str, max_lines: int = 38) -> list[str]:
    lines = read_lines(relative)
    start = next((i for i, line in enumerate(lines) if marker in line), 0)
    return lines[start : start + max_lines]


def extract_between(relative: str, start_marker: str, end_marker: str | None = None, max_lines: int = 80) -> list[str]:
    lines = read_lines(relative)
    start = next((i for i, line in enumerate(lines) if start_marker in line), 0)
    end = start + max_lines
    if end_marker:
        for i in range(start + 1, min(len(lines), start + max_lines)):
            if end_marker in lines[i]:
                end = i
                break
    return lines[start:end]


def wrap_para(text: str, width: int = 86) -> list[str]:
    result: list[str] = []
    for paragraph in text.split("\n"):
        result.extend(textwrap.wrap(paragraph, width=width) or [""])
    return result


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, accent: str) -> None:
    draw.rounded_rectangle((42, 34, 1558, 142), radius=20, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((42, 34, 58, 142), fill=accent)
    draw.text((84, 52), title, font=FONT_UI_BOLD, fill=INK)
    draw.text((84, 98), subtitle, font=FONT_UI_SMALL, fill=MUTED)


def draw_code_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    lines: list[str],
    start_line: int = 1,
    accent: str = BLUE,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x2, y1 + 52), fill="#eef4ff")
    draw.rectangle((x1, y1, x1 + 12, y2), fill=accent)
    draw.text((x1 + 28, y1 + 13), label, font=FONT_UI_SMALL, fill=INK)
    y = y1 + 74
    max_chars = max(62, int((x2 - x1 - 92) / 12))
    for idx, line in enumerate(lines):
        if y > y2 - 32:
            draw.text((x1 + 62, y), "...", font=FONT_MONO, fill=MUTED)
            break
        compact = line.expandtabs(4)
        if len(compact) > max_chars:
            compact = compact[: max_chars - 3] + "..."
        draw.text((x1 + 24, y), f"{start_line + idx:>3}", font=FONT_MONO_SMALL, fill="#94a3b8")
        draw.text((x1 + 74, y), compact, font=FONT_MONO_SMALL, fill=INK)
        y += 24


def save_code_image(
    filename: str,
    title: str,
    subtitle: str,
    panels: list[tuple[str, list[str], str]],
    accent: str,
) -> None:
    img = Image.new("RGB", (1600, 1000), BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, subtitle, accent)
    if len(panels) == 1:
        draw_code_panel(draw, (60, 180, 1540, 940), panels[0][0], panels[0][1], accent=panels[0][2])
    elif len(panels) == 2:
        draw_code_panel(draw, (60, 180, 780, 940), panels[0][0], panels[0][1], accent=panels[0][2])
        draw_code_panel(draw, (820, 180, 1540, 940), panels[1][0], panels[1][1], accent=panels[1][2])
    else:
        y = 180
        for label, lines, color in panels[:3]:
            draw_code_panel(draw, (60, y, 1540, y + 235), label, lines[:6], accent=color)
            y += 255
    img.save(OUT / filename)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#64748b") -> None:
    draw.line((start, end), fill=color, width=5)
    x, y = end
    draw.polygon([(x, y), (x - 14, y - 9), (x - 14, y + 9)], fill=color)


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, body: str, color: str) -> None:
    draw.rounded_rectangle(box, radius=18, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((box[0], box[1], box[0] + 12, box[3]), fill=color)
    draw.text((box[0] + 34, box[1] + 24), title, font=FONT_UI_BOLD, fill=INK)
    y = box[1] + 76
    wrap_width = max(22, int((box[2] - box[0] - 80) / 11))
    for line in wrap_para(body, wrap_width):
        draw.text((box[0] + 34, y), line, font=FONT_UI_SMALL, fill=MUTED)
        y += 32


def save_flow_image(filename: str, title: str, subtitle: str, boxes: list[tuple[str, str, str]]) -> None:
    img = Image.new("RGB", (1600, 920), BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, subtitle, BLUE)
    x_positions = [70, 460, 850, 1240]
    y = 280
    for idx, (box_title, body, color) in enumerate(boxes):
        draw_box(draw, (x_positions[idx], y, x_positions[idx] + 300, y + 270), box_title, body, color)
        if idx < len(boxes) - 1:
            draw_arrow(draw, (x_positions[idx] + 315, y + 135), (x_positions[idx + 1] - 16, y + 135))
    img.save(OUT / filename)


def save_tree_image() -> None:
    img = Image.new("RGB", (1600, 1000), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH04 - Cấu trúc thư mục theo 3 lớp",
        "Minh chứng dự án đã tách UI, xử lý nghiệp vụ, truy cập dữ liệu và model.",
        PURPLE,
    )
    tree = [
        "HSMS/",
        "  ui/",
        "    app.py",
        "    views/",
        "      dashboard_view.py",
        "      students_view.py",
        "      classes_view.py",
        "      teachers_view.py",
        "    components/",
        "      data_table.py, metric_card.py, chart_panel.py",
        "  services/",
        "    hoc_sinh_service.py",
        "    lop_service.py",
        "    giao_vien_service.py",
        "    dashboard_service.py",
        "  dao/",
        "    db.py",
        "    hoc_sinh_dao.py",
        "    lop_dao.py",
        "    giao_vien_dao.py",
        "  models/",
        "    hoc_sinh.py, lop.py, giao_vien.py",
        "  database/",
        "    init_db.sql",
        "  data/",
        "    hsms.sqlite3",
    ]
    draw_code_panel(draw, (70, 180, 850, 920), "Cây thư mục chính", tree, accent=PURPLE)
    notes = [
        ("UI Layer", "Các màn hình CustomTkinter chỉ nhận nhập liệu và hiển thị dữ liệu.", BLUE),
        ("Business Layer", "Service kiểm tra ràng buộc, sinh mã, gọi DAO và ghi activity log.", GREEN),
        ("Data Access Layer", "DAO gom toàn bộ câu SQL, kết nối SQLite qua dao/db.py.", AMBER),
        ("Model/DTO", "Dataclass HocSinhInfo, LopInfo, GiaoVienInfo truyền dữ liệu giữa các lớp.", RED),
    ]
    y = 205
    for title, body, color in notes:
        draw_box(draw, (910, y, 1530, y + 150), title, body, color)
        y += 175
    img.save(OUT / "BTTH04_01_project_3layer_tree.png")


def write_captions() -> None:
    captions = """# Chú thích ảnh minh chứng theo bài thực hành

## Bài thực hành 2 - Database và CRUD

1. `BTTH02_01_database_schema_hocsinh_lop.png` - Hình minh chứng cấu trúc cơ sở dữ liệu với hai bảng chính `LOP` và `HOCSINH`, khóa chính và khóa ngoại đúng theo yêu cầu quản lý học sinh theo lớp.
2. `BTTH02_02_student_dao_crud_sql.png` - Hình minh chứng các thao tác CRUD ở tầng DAO: thêm, cập nhật và xóa học sinh bằng câu lệnh SQL có tham số.
3. `BTTH02_03_crud_flow.png` - Sơ đồ mô tả luồng CRUD cơ bản: người dùng nhập form, hệ thống kiểm tra dữ liệu, DAO ghi xuống bảng và danh sách được tải lại.

## Bài thực hành 3 - Tách đối tượng và xử lý form

4. `BTTH03_01_models_hocsinh_lop.png` - Hình minh chứng lớp đối tượng `HocSinhInfo` và `LopInfo`, dùng để đóng gói dữ liệu thay vì truyền rời rạc từng biến.
5. `BTTH03_02_form_to_objects_flow.png` - Sơ đồ mô tả luồng từ màn hình quản lý học sinh sang object, service và danh sách hiển thị.
6. `BTTH03_03_students_form_handling_code.png` - Hình minh chứng phần xử lý form: chuyển dữ liệu form thành `HocSinhInfo`, chọn dòng để sửa và lưu dữ liệu.

## Bài thực hành 4 - Kiến trúc 3 lớp và mở rộng hệ thống

7. `BTTH04_01_project_3layer_tree.png` - Hình minh chứng cấu trúc thư mục đã tách thành `ui`, `services`, `dao`, `models`, `database`.
8. `BTTH04_02_architecture_3layer_diagram.png` - Sơ đồ kiến trúc 3 lớp của hệ thống: giao diện, xử lý nghiệp vụ, truy cập dữ liệu và database.
9. `BTTH04_03_service_dao_example.png` - Hình minh chứng service kiểm tra nghiệp vụ và gọi DAO, trong khi DAO chịu trách nhiệm làm việc trực tiếp với SQL/database.
"""
    (OUT / "HSMS_report_evidence_captions.md").write_text(captions, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    schema_lines = extract_between("database/init_db.sql", "CREATE TABLE IF NOT EXISTS LOP", "CREATE TABLE IF NOT EXISTS GIAOVIEN", 42)
    dao_crud = (
        extract_block("dao/hoc_sinh_dao.py", "def insert", 10)
        + [""]
        + extract_block("dao/hoc_sinh_dao.py", "def update", 10)
        + [""]
        + extract_block("dao/hoc_sinh_dao.py", "def delete", 7)
    )
    hoc_sinh_model = read_lines("models/hoc_sinh.py")
    lop_model = read_lines("models/lop.py")
    form_code = (
        extract_block("ui/views/students_view.py", "def _form_to_model", 20)
        + [""]
        + extract_block("ui/views/students_view.py", "def _on_row_select", 7)
        + [""]
        + extract_block("ui/views/students_view.py", "def _save", 24)
    )
    service_code = extract_between("services/hoc_sinh_service.py", "def _validate", "def list_students", 55)
    dao_code = extract_block("dao/hoc_sinh_dao.py", "def insert", 24)

    save_code_image(
        "BTTH02_01_database_schema_hocsinh_lop.png",
        "BTTH02 - Thiết kế database QLHOCSINH",
        "Tập trung vào bảng LOP, HOCSINH, khóa chính, khóa ngoại và dữ liệu nền.",
        [("database/init_db.sql", schema_lines, BLUE)],
        BLUE,
    )
    save_code_image(
        "BTTH02_02_student_dao_crud_sql.png",
        "BTTH02 - Cài đặt CRUD học sinh bằng SQL",
        "Minh chứng các thao tác thêm, sửa, xóa dữ liệu học sinh ở DAO.",
        [("dao/hoc_sinh_dao.py - insert/update/delete", dao_crud, GREEN)],
        GREEN,
    )
    save_flow_image(
        "BTTH02_03_crud_flow.png",
        "BTTH02 - Luồng CRUD một chức năng quản lý học sinh",
        "Ảnh này dùng để giải thích tiến độ xây dựng form nhập liệu, lưu, xóa và tải lại danh sách.",
        [
            ("Form nhập liệu", "Mã HS, họ tên, giới tính, ngày sinh, địa chỉ, điểm TB, lớp.", BLUE),
            ("Kiểm tra dữ liệu", "Không để trống trường bắt buộc, điểm TB từ 0 đến 10.", AMBER),
            ("DAO + SQL", "INSERT, UPDATE, DELETE chạy với tham số để ghi vào SQLite.", GREEN),
            ("Bảng dữ liệu", "Danh sách học sinh được refresh để hiển thị kết quả mới.", PURPLE),
        ],
    )

    save_code_image(
        "BTTH03_01_models_hocsinh_lop.png",
        "BTTH03 - Tách lớp đối tượng HocSinh và Lop",
        "Minh chứng dữ liệu được đóng gói bằng dataclass trước khi truyền qua các lớp xử lý.",
        [("models/hoc_sinh.py", hoc_sinh_model, BLUE), ("models/lop.py", lop_model, PURPLE)],
        BLUE,
    )
    save_flow_image(
        "BTTH03_02_form_to_objects_flow.png",
        "BTTH03 - Từ form giao diện sang object và service",
        "Khác BTTH02 ở chỗ dữ liệu form không đi thẳng vào SQL mà được đóng gói thành object.",
        [
            ("StudentsView", "Người dùng nhập form, chọn dòng trong bảng, lọc theo lớp.", BLUE),
            ("HocSinhInfo", "Object chứa MaHS, HoTen, GioiTinh, NgaySinh, DiaChi, DiemTB, MaLop.", PURPLE),
            ("Service", "Kiểm tra ràng buộc, quyết định thêm mới hoặc cập nhật.", GREEN),
            ("DAO", "Nhận object hợp lệ rồi thực thi SQL tương ứng.", AMBER),
        ],
    )
    save_code_image(
        "BTTH03_03_students_form_handling_code.png",
        "BTTH03 - Xử lý form, chọn dòng và lưu học sinh",
        "Minh chứng phần form quản lý học sinh đã kết nối với object và service.",
        [("ui/views/students_view.py", form_code, AMBER)],
        AMBER,
    )

    save_tree_image()
    save_flow_image(
        "BTTH04_02_architecture_3layer_diagram.png",
        "BTTH04 - Sơ đồ kiến trúc 3 lớp của hệ thống",
        "Minh chứng hệ thống đã mở rộng từ CRUD sang cấu trúc dễ bảo trì và phát triển thêm.",
        [
            ("UI Layer", "Dashboard, quản lý học sinh, lớp học, giáo viên; chỉ hiển thị và nhận thao tác.", BLUE),
            ("Business Layer", "Service validate dữ liệu, sinh mã tự động, kiểm tra quy tắc xóa/sửa.", GREEN),
            ("DAO Layer", "Tập trung câu SQL và hàm truy cập dữ liệu.", AMBER),
            ("Database", "SQLite lưu LOP, HOCSINH, GIAOVIEN, ACTIVITY_LOG.", PURPLE),
        ],
    )
    save_code_image(
        "BTTH04_03_service_dao_example.png",
        "BTTH04 - Service gọi DAO theo kiến trúc 3 lớp",
        "Minh chứng service xử lý nghiệp vụ còn DAO làm việc trực tiếp với database.",
        [("services/hoc_sinh_service.py", service_code, GREEN), ("dao/hoc_sinh_dao.py", dao_code, AMBER)],
        PURPLE,
    )
    write_captions()


if __name__ == "__main__":
    main()
