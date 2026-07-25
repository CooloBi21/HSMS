"""
Sinh hình minh chứng BTTH03 (Mô hình 2 lớp — tách đối tượng + Form).
Chạy: python ReportAssets/BTTH03/generate_btth03_assets.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent

# Theme tím — phân biệt với BTTH02 (xanh navy) và BTTH04 (sẽ dùng xanh lá/teal)
BG = "#faf5ff"
HEADER_BG = "#5b21b6"
HEADER_FG = "#ffffff"
BORDER = "#d8b4fe"
TEXT = "#1e1b4b"
MUTED = "#6b7280"
ACCENT = "#7c3aed"
ACCENT2 = "#a855f7"
LINE_NUM = "#a78bfa"
HIGHLIGHT = "#ede9fe"
BOX_UI = "#ddd6fe"
BOX_BL = "#c4b5fd"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for fname in (["consolab.ttf", "consola.ttf"] if bold else ["consola.ttf", "CascadiaMono.ttf", "cour.ttf"]):
        path = Path("C:/Windows/Fonts") / fname
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def _text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _wrap_lines(text, draw, font, max_width):
    lines = []
    for raw in text.splitlines():
        if not raw.strip():
            lines.append("")
            continue
        words, current = raw.split(" "), ""
        for w in words:
            trial = w if not current else f"{current} {w}"
            if _text_size(draw, trial, font)[0] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
    return lines


def render_code_image(filename, title, subtitle, filepath, code, highlight_lines=None, width=1100):
    highlight_lines = highlight_lines or set()
    pad, line_h = 24, 22
    font, font_sm = _font(15), _font(12)
    font_title, font_sub = _font(18, True), _font(13)

    dummy = Image.new("RGB", (width, 100), BG)
    d = ImageDraw.Draw(dummy)
    wrapped = []
    for i, line in enumerate(code.splitlines(), 1):
        for wl in _wrap_lines(line, d, font, width - pad * 2 - 50):
            wrapped.append((wl, i))

    header_h = 88
    h = header_h + len(wrapped) * line_h + pad * 2 + 20
    img = Image.new("RGB", (width, h), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((12, 12, width - 12, h - 12), radius=12, fill=BG, outline=BORDER, width=2)
    draw.rounded_rectangle((12, 12, width - 12, header_h), radius=12, fill=HEADER_BG)
    draw.rectangle((12, header_h - 16, width - 12, header_h), fill=HEADER_BG)
    draw.text((pad + 8, 22), title, fill=HEADER_FG, font=font_title)
    draw.text((pad + 8, 50), subtitle, fill="#e9d5ff", font=font_sub)
    draw.text((width - pad - 8, 50), filepath, fill="#ddd6fe", font=font_sm, anchor="ra")

    y = header_h + pad
    for text, src_line in wrapped:
        if src_line in highlight_lines:
            draw.rectangle((pad, y - 2, width - pad, y + line_h - 4), fill=HIGHLIGHT)
        draw.text((pad, y), f"{src_line:>3}", fill=LINE_NUM, font=font_sm)
        draw.text((pad + 44, y), text, fill=TEXT, font=font)
        y += line_h

    path = OUT / filename
    img.save(path, "PNG")
    return path


def render_two_layer_diagram(filename: str) -> Path:
    w, h = 1040, 560
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    ft = _font(20, True)
    fs = _font(14)
    fb = _font(15, True)

    draw.rounded_rectangle((8, 8, w - 8, h - 8), radius=12, outline=BORDER, width=2, fill=BG)
    draw.text((32, 24), "BTTH03 — Mô hình 2 lớp (Form + Lớp xử lý đối tượng)", fill=TEXT, font=ft)
    draw.text((32, 54), "Tương đương: FormHocSinh → HocSinh / Lop (PDF bài thực hành 3)", fill=MUTED, font=fs)

    def box(x, y, bw, bh, title, lines, fill):
        draw.rounded_rectangle((x, y, x + bw, y + bh), radius=10, outline=ACCENT, width=2, fill=fill)
        draw.rectangle((x, y, x + bw, y + 38), fill=ACCENT)
        draw.text((x + 14, y + 8), title, fill="#fff", font=fb)
        cy = y + 48
        for line in lines:
            draw.text((x + 14, cy), line, fill=TEXT, font=fs)
            cy += 22

    box(80, 100, 880, 90, "Lớp 1 — Giao diện (Form)", [
        "StudentsView  —  form nhập HS, lưới danh sách, ComboBox lớp, tìm kiếm/lọc",
        "ClassesView   —  form quản lý lớp (Lop) riêng biệt",
    ], BOX_UI)

    # arrows
    for ax in (520,):
        draw.line([(ax, 190), (ax, 230)], fill=ACCENT2, width=3)
        draw.polygon([(ax, 230), (ax - 8, 218), (ax + 8, 218)], fill=ACCENT2)
    draw.text((540, 200), "gọi phương thức", fill=ACCENT, font=fs)

    box(60, 240, 400, 200, "Lớp 2a — HocSinh (đối tượng + xử lý)", [
        "HocSinhInfo   —  ma_hs, ho_ten, gioi_tinh, ...",
        "student_service.list_students(ma_lop, search)",
        "student_service.create / update / delete",
        "student_service.get_student(ma_hs)",
    ], BOX_BL)

    box(560, 240, 400, 200, "Lớp 2b — Lop (đối tượng + xử lý)", [
        "LopInfo       —  ma_lop, ten_lop, khoi",
        "school_class_service.list_classes()",
        "school_class_service.create / update / delete",
        "school_class_service.get_class(ma_lop)",
    ], BOX_BL)

    draw.line([(520, 440), (520, 480)], fill=MUTED, width=2)
    draw.polygon([(520, 480), (512, 468), (528, 468)], fill=MUTED)
    draw.rounded_rectangle((180, 490, 860, 540), radius=8, outline=MUTED, width=1, fill="#f5f3ff")
    draw.text(
        (200, 502),
        "Dữ liệu HOCSINH & LOP (CSDL) — đã thiết lập ở BTTH02; BTTH03 tập trung tách lớp xử lý khỏi Form",
        fill=MUTED,
        font=fs,
    )

    path = OUT / filename
    img.save(path, "PNG")
    return path


def render_sequence_diagram(filename: str) -> Path:
    """Luồng chọn dòng lưới → nạp form (yêu cầu BTTH03)."""
    w, h = 1000, 420
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    ft, fs, fb = _font(18, True), _font(13), _font(14, True)

    draw.rounded_rectangle((8, 8, w - 8, h - 8), radius=12, outline=BORDER, width=2, fill=BG)
    draw.text((32, 20), "BTTH03 — Luồng sự kiện Form ↔ Lớp HocSinh", fill=TEXT, font=ft)

    steps = [
        ("1", "Form Load / refresh()", "StudentsView gọi student_service.list_students() và school_class_service.list_classes()"),
        ("2", "Lọc theo lớp", "list_students(ma_lop=...) — hiển thị HS thuộc lớp đã chọn trên ComboBox"),
        ("3", "Chọn dòng (SelectionChanged)", "_on_row_select → student_service.get_student(MaHS)"),
        ("4", "Nạp form", "_fill_form(HocSinhInfo) — đưa dữ liệu từ lớp HocSinh lên các control"),
        ("5", "Lưu / Xóa", "create_student / update_student / delete_student qua student_service"),
    ]
    y = 58
    for num, title, desc in steps:
        draw.ellipse((40, y + 4, 68, y + 32), fill=ACCENT)
        draw.text((48, y + 8), num, fill="#fff", font=fb)
        draw.text((82, y + 4), title, fill=TEXT, font=fb)
        draw.text((82, y + 26), desc, fill=MUTED, font=fs)
        if y < 320:
            draw.line([(54, y + 34), (54, y + 52)], fill=ACCENT2, width=2)
        y += 58

    path = OUT / filename
    img.save(path, "PNG")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    hocsinh_model = """# models/hoc_sinh.py — Lớp đại diện dữ liệu học sinh (HocSinhInfo)
@dataclass
class HocSinhInfo:
    ma_hs: str
    ho_ten: str
    gioi_tinh: Optional[int] = None
    ngay_sinh: Optional[str] = None
    dia_chi: Optional[str] = None
    diem_tb: Optional[float] = None
    ma_lop: Optional[str] = None

    @property
    def gioi_tinh_text(self) -> str:
        if self.gioi_tinh == 1: return "Nam"
        if self.gioi_tinh == 0: return "Nữ"
        return """""

    lop_model = """# models/lop.py — Lớp đại diện dữ liệu lớp học (LopInfo)
@dataclass
class LopInfo:
    ma_lop: str
    ten_lop: str
    khoi: Optional[str] = None"""

    service_code = """# services/student_service.py — Lớp xử lý nghiệp vụ HocSinh (tầng 2)

def list_students(ma_lop=None, search=None) -> List[HocSinhInfo]:
    return student_dao.get_all(ma_lop=ma_lop, search=search)

def get_student(ma_hs: str) -> Optional[HocSinhInfo]:
    return student_dao.get_by_id(ma_hs)

def create_student(hs: HocSinhInfo) -> HocSinhInfo:
    _validate(hs, is_update=False)
    student_dao.insert(hs)
    return hs

def update_student(hs: HocSinhInfo) -> HocSinhInfo:
    _validate(hs, is_update=True)
    student_dao.update(hs)
    return hs

def delete_student(ma_hs: str) -> bool:
    return student_dao.delete(ma_hs)"""

    form_code = """# ui/views/students_view.py — Form gọi lớp xử lý, không tự thao tác DB

def _on_row_select(self, values: tuple) -> None:
    hs = student_service.get_student(values[0])
    if hs:
        self._fill_form(hs)          # SelectionChanged → nạp form

def _fill_form(self, hs: HocSinhInfo) -> None:
    self._ho_ten.insert(0, hs.ho_ten)
    self._gioi_tinh.set(hs.gioi_tinh_text)
    self._ma_lop.set(...)            # ComboBox lớp

def refresh(self) -> None:
    classes = school_class_service.list_classes()
    self._load_class_options()       # nạp ComboBox từ lớp Lop
    students = student_service.list_students(
        ma_lop=ma_lop, search=search)  # lọc / tìm trên lưới"""

    files = [
        render_two_layer_diagram("BTTH03_01_two_layer_diagram.png"),
        render_sequence_diagram("BTTH03_02_form_event_flow.png"),
        render_code_image(
            "BTTH03_03_model_hocsinh.png",
            "BTTH03 — Lớp đối tượng HocSinhInfo",
            "Đại diện dữ liệu một học sinh (tương đương class HocSinh PDF)",
            "models/hoc_sinh.py",
            hocsinh_model,
            highlight_lines={2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        ),
        render_code_image(
            "BTTH03_04_model_lop.png",
            "BTTH03 — Lớp đối tượng LopInfo",
            "Đại diện dữ liệu một lớp học (tương đương class Lop PDF)",
            "models/lop.py",
            lop_model,
            highlight_lines={2, 3, 4, 5, 6},
        ),
        render_code_image(
            "BTTH03_05_service_hocsinh.png",
            "BTTH03 — Lớp xử lý HocSinh (Business)",
            "Form gọi service — không xử lý SQL trực tiếp trên Form",
            "services/student_service.py",
            service_code,
            highlight_lines={3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22},
        ),
        render_code_image(
            "BTTH03_06_form_calls_service.png",
            "BTTH03 — Form ↔ Lớp xử lý",
            "Chọn dòng lưới, nạp form, lọc theo lớp",
            "ui/views/students_view.py",
            form_code,
            highlight_lines={3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19},
        ),
    ]

    captions = """# Chú thích hình BTTH03 — Mô hình 2 lớp

## Hình minh chứng code / sơ đồ (chỉ BTTH03 — theme tím)

| File | Chú thích Word |
|------|----------------|
| `BTTH03_01_two_layer_diagram.png` | Hình 1. Sơ đồ mô hình 2 lớp: lớp giao diện (StudentsView) và lớp xử lý đối tượng HocSinh/Lop. |
| `BTTH03_02_form_event_flow.png` | Hình 2. Luồng sự kiện: load danh sách, lọc theo lớp, chọn dòng, nạp form, lưu/xóa. |
| `BTTH03_03_model_hocsinh.png` | Hình 3. Lớp HocSinhInfo — đại diện thuộc tính học sinh. |
| `BTTH03_04_model_lop.png` | Hình 4. Lớp LopInfo — đại diện thuộc tính lớp học. |
| `BTTH03_05_service_hocsinh.png` | Hình 5. Lớp xử lý student_service: lấy danh sách, thêm, sửa, xóa. |
| `BTTH03_06_form_calls_service.png` | Hình 6. Form gọi service khi chọn dòng và refresh danh sách. |

## Ảnh giao diện dùng chung — caption BTTH03 (KHÁC BTTH02)

| Ảnh | Caption BTTH03 |
|-----|----------------|
| `02_students_overview.png` | FormHocSinh: giao diện gọi HocSinhInfo và school_class_service để hiển thị danh sách và ComboBox lớp. |
| `04_students_select_edit.png` | Sự kiện chọn dòng trên lưới (SelectionChanged): dữ liệu HocSinhInfo được nạp lên form. |
| `05_students_search_filter.png` | Lọc học sinh theo lớp — gọi list_students(ma_lop=...) từ lớp xử lý HocSinh. |
| `06_classes_overview.png` | Quản lý lớp Lop riêng biệt — lớp giao diện làm việc với LopInfo qua school_class_service. |

## Không dùng ở BTTH03

Dashboard, Giáo viên, Dark mode → để dành BTTH04.

## Ghi chú cuối bài (1 câu)

> So với BTTH02 tập trung CSDL/CRUD, BTTH03 minh chứng việc tách Form và lớp xử lý đối tượng HocSinh/Lop theo mô hình 2 lớp.
"""
    (OUT / "BTTH03_captions.md").write_text(captions, encoding="utf-8")

    print("Generated BTTH03 assets:")
    for p in files:
        print(f"  {p}")


if __name__ == "__main__":
    main()
