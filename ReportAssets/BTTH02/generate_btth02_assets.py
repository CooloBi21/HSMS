"""
Sinh hình minh chứng BTTH02 (CSDL + CRUD) — không phải ảnh giao diện chung.
Chạy: python ReportAssets/BTTH02/generate_btth02_assets.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

# Màu theme báo cáo (nền sáng, dễ in Word)
BG = "#f8fafc"
HEADER_BG = "#1e3a5f"
HEADER_FG = "#ffffff"
BORDER = "#cbd5e1"
TEXT = "#0f172a"
MUTED = "#64748b"
ACCENT = "#2563eb"
LINE_NUM = "#94a3b8"
HIGHLIGHT = "#dbeafe"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        ("Consolas", "consolab.ttf" if bold else "consola.ttf"),
        ("Cascadia Mono", "CascadiaMono.ttf"),
        ("Courier New", "cour.ttf"),
    ]
    windir = Path("C:/Windows/Fonts")
    for family, fname in candidates:
        path = windir / fname
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _wrap_lines(text: str, draw, font, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        if not raw.strip():
            lines.append("")
            continue
        words = raw.split(" ")
        current = ""
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


def render_code_image(
    filename: str,
    title: str,
    subtitle: str,
    filepath: str,
    code: str,
    highlight_lines: set[int] | None = None,
    width: int = 1100,
) -> Path:
    highlight_lines = highlight_lines or set()
    pad = 24
    line_h = 22
    font = _font(15)
    font_sm = _font(12)
    font_title = _font(18, bold=True)
    font_sub = _font(13)

    dummy = Image.new("RGB", (width, 100), BG)
    d = ImageDraw.Draw(dummy)
    code_lines = code.splitlines()
    max_code_w = width - pad * 2 - 50
    wrapped: list[tuple[str, int | None]] = []
    for i, line in enumerate(code_lines, start=1):
        for wl in _wrap_lines(line, d, font, max_code_w):
            wrapped.append((wl, i if wl == line or not line else None))

    body_h = len(wrapped) * line_h + pad * 2
    header_h = 88
    h = header_h + body_h + 20

    img = Image.new("RGB", (width, h), BG)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((12, 12, width - 12, h - 12), radius=12, fill=BG, outline=BORDER, width=2)
    draw.rounded_rectangle((12, 12, width - 12, header_h), radius=12, fill=HEADER_BG)
    draw.rectangle((12, header_h - 16, width - 12, header_h), fill=HEADER_BG)

    draw.text((pad + 8, 22), title, fill=HEADER_FG, font=font_title)
    draw.text((pad + 8, 50), subtitle, fill="#cbd5e1", font=font_sub)
    draw.text((width - pad - 8, 50), filepath, fill="#93c5fd", font=font_sm, anchor="ra")

    y = header_h + pad
    for text, src_line in wrapped:
        if src_line and src_line in highlight_lines:
            draw.rectangle((pad, y - 2, width - pad, y + line_h - 4), fill=HIGHLIGHT)
        if src_line:
            draw.text((pad, y), f"{src_line:>3}", fill=LINE_NUM, font=font_sm)
        draw.text((pad + 44, y), text, fill=TEXT, font=font)
        y += line_h

    path = OUT / filename
    img.save(path, "PNG", optimize=True)
    return path


def render_er_diagram(filename: str) -> Path:
    w, h = 1000, 520
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    font = _font(14)
    font_b = _font(16, bold=True)
    font_t = _font(20, bold=True)

    draw.rounded_rectangle((8, 8, w - 8, h - 8), radius=12, outline=BORDER, width=2, fill=BG)
    draw.text((32, 24), "CSDL QLHOCSINH — Sơ đồ bảng HOCSINH & LOP (SQLite)", fill=TEXT, font=font_t)
    draw.text((32, 56), "Tương ứng file database/init_db.sql · data/hsms.db", fill=MUTED, font=font)

    def table_box(x, y, tw, th, name, rows):
        draw.rounded_rectangle((x, y, x + tw, y + th), radius=10, outline=ACCENT, width=2, fill="#ffffff")
        draw.rectangle((x, y, x + tw, y + 36), fill=ACCENT)
        draw.text((x + 12, y + 8), name, fill="#ffffff", font=font_b)
        cy = y + 44
        for col, typ, note in rows:
            line = f"{col}  {typ}"
            if note:
                line += f"  — {note}"
            draw.text((x + 12, cy), line, fill=TEXT, font=font)
            cy += 24

    table_box(
        60, 100, 400, 200, "LOP",
        [
            ("MaLop", "TEXT", "PK"),
            ("TenLop", "TEXT", "NOT NULL"),
            ("Khoi", "TEXT", ""),
        ],
    )
    table_box(
        520, 100, 420, 280, "HOCSINH",
        [
            ("MaHS", "TEXT", "PK"),
            ("HoTen", "TEXT", "NOT NULL"),
            ("GioiTinh", "INTEGER", "0=Nữ, 1=Nam"),
            ("NgaySinh", "TEXT", ""),
            ("DiaChi", "TEXT", ""),
            ("DiemTB", "REAL", ""),
            ("MaLop", "TEXT", "FK → LOP"),
        ],
    )

    # FK arrow
    ax1, ay1 = 460, 200
    ax2, ay2 = 520, 200
    draw.line([(ax1, ay1), (ax2, ay2)], fill=ACCENT, width=3)
    draw.polygon([(ax2, ay2), (ax2 - 12, ay2 - 6), (ax2 - 12, ay2 + 6)], fill=ACCENT)
    draw.text((430, 168), "MaLop (FK)", fill=ACCENT, font=font)

    draw.text(
        (60, 420),
        "Quan hệ: Một lớp (LOP) có nhiều học sinh (HOCSINH). Xóa lớp → MaLop học sinh = NULL (ON DELETE SET NULL).",
        fill=MUTED,
        font=font,
    )

    path = OUT / filename
    img.save(path, "PNG")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    schema_sql = """-- database/init_db.sql — Bảng LOP và HOCSINH (CSDL QLHOCSINH)
CREATE TABLE IF NOT EXISTS LOP (
    MaLop   TEXT PRIMARY KEY,
    TenLop  TEXT NOT NULL,
    Khoi    TEXT
);

CREATE TABLE IF NOT EXISTS HOCSINH (
    MaHS      TEXT PRIMARY KEY,
    HoTen     TEXT NOT NULL,
    GioiTinh  INTEGER,
    NgaySinh  TEXT,
    DiaChi    TEXT,
    DiemTB    REAL,
    MaLop     TEXT,
    FOREIGN KEY (MaLop) REFERENCES LOP(MaLop) ON DELETE SET NULL
);"""

    crud_code = """# dao/student_dao.py — Thao tác CRUD trên bảng HOCSINH

def insert(hs: HocSinhInfo) -> None:
    with get_connection() as conn:
        conn.execute(
            \"\"\"INSERT INTO HOCSINH (MaHS, HoTen, GioiTinh, NgaySinh,
               DiaChi, DiemTB, MaLop)
               VALUES (?, ?, ?, ?, ?, ?, ?)\"\"\",
            (hs.ma_hs, hs.ho_ten, hs.gioi_tinh, hs.ngay_sinh,
             hs.dia_chi, hs.diem_tb, hs.ma_lop),
        )
        conn.commit()

def update(hs: HocSinhInfo) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            \"\"\"UPDATE HOCSINH SET HoTen=?, GioiTinh=?, NgaySinh=?,
               DiaChi=?, DiemTB=?, MaLop=? WHERE MaHS=?\"\"\",
            (hs.ho_ten, hs.gioi_tinh, hs.ngay_sinh, hs.dia_chi,
             hs.diem_tb, hs.ma_lop, hs.ma_hs),
        )
        conn.commit()
        return cur.rowcount > 0

def delete(ma_hs: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM HOCSINH WHERE MaHS = ?", (ma_hs,))
        conn.commit()
        return cur.rowcount > 0"""

    combobox_code = """# dao/school_class_dao.py — Đọc danh sách lớp từ CSDL
def get_all() -> List[LopInfo]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM LOP ORDER BY Khoi, TenLop"
        ).fetchall()
    return [_row_to_info(r) for r in rows]

# ui/views/students_view.py — Nạp ComboBox lớp trên Form nhập học sinh
def _load_class_options(self) -> None:
    classes = school_class_service.list_classes()  # → gọi DAO đọc bảng LOP
    self._class_map = {
        f"{c.ten_lop} ({c.ma_lop})": c.ma_lop for c in classes
    }
    lop_values = list(self._class_map.keys())
    self._ma_lop.configure(values=lop_values)          # ComboBox form
    self._filter_lop.configure(values=["Tất cả lớp"] + lop_values)"""

    files = [
        render_er_diagram("BTTH02_01_er_diagram_lop_hocsinh.png"),
        render_code_image(
            "BTTH02_02_schema_init_db.png",
            "BTTH02 — Cấu trúc bảng HOCSINH và LOP",
            "Minh chứng thiết kế CSDL QLHOCSINH (SQLite)",
            "database/init_db.sql",
            schema_sql,
            highlight_lines={2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17},
        ),
        render_code_image(
            "BTTH02_03_dao_crud_hocsinh.png",
            "BTTH02 — Thêm, cập nhật, xóa học sinh",
            "Truy vấn tham số hóa INSERT / UPDATE / DELETE",
            "dao/student_dao.py",
            crud_code,
            highlight_lines={3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29},
        ),
        render_code_image(
            "BTTH02_04_load_combobox_lop.png",
            "BTTH02 — Load danh sách lớp vào ComboBox",
            "Form Load: đọc LOP → hiển thị trên ComboBox chọn lớp",
            "students_view.py + school_class_dao.py",
            combobox_code,
            highlight_lines={2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17},
        ),
    ]

    captions = """# Chú thích hình BTTH02 — CSDL & CRUD

Dùng kèm ảnh giao diện từ `feature-screenshots/` nhưng **caption phải nhấn CSDL/CRUD**, không nhấn kiến trúc 3 lớp.

## Hình minh chứng code / CSDL (chỉ BTTH02)

| File | Chú thích đề xuất (Word) |
|------|--------------------------|
| `BTTH02_01_er_diagram_lop_hocsinh.png` | Hình 1. Sơ đồ quan hệ hai bảng LOP và HOCSINH trong CSDL QLHOCSINH (SQLite), thể hiện khóa chính MaLop/MaHS và khóa ngoại MaLop. |
| `BTTH02_02_schema_init_db.png` | Hình 2. Đoạn mã SQL khai báo bảng LOP và HOCSINH trong file `database/init_db.sql`. |
| `BTTH02_03_dao_crud_hocsinh.png` | Hình 3. Đoạn xử lý thêm mới (INSERT), cập nhật (UPDATE) và xóa (DELETE) dữ liệu học sinh trên bảng HOCSINH. |
| `BTTH02_04_load_combobox_lop.png` | Hình 4. Đoạn đọc danh sách lớp từ CSDL và nạp vào ComboBox trên form nhập học sinh (tương đương Form_Load trong bài thực hành). |

## Gợi ý caption khi dùng lại ảnh giao diện chung

| Ảnh giao diện | Caption BTTH02 (khác BTTH03/04) |
|---------------|----------------------------------|
| `02_students_overview.png` | Màn hình nhập và quản lý dữ liệu học sinh: các trường MaHS, HoTen, GioiTinh, NgaySinh, DiaChi, DiemTB, MaLop và lưới danh sách. |
| `03_students_add_new_autocode.png` | Thao tác thêm mới học sinh — dữ liệu được ghi vào bảng HOCSINH. |
| `04_students_select_edit.png` | Chọn dòng trên lưới để nạp dữ liệu lên form và thực hiện UPDATE. |
| `05_students_search_filter.png` | Tìm kiếm/lọc danh sách học sinh theo lớp (truy vấn có điều kiện trên HOCSINH). |
| `06_classes_overview.png` | Quản lý bảng LOP — dữ liệu lớp phục vụ ComboBox chọn lớp cho học sinh. |

## Câu ghi chú kiến trúc (1 dòng cuối bài)

> Trong phiên bản hiện tại, hệ thống đã được nâng cấp kiến trúc để dễ bảo trì hơn; phần minh chứng BTTH02 tập trung vào CSDL và các thao tác CRUD cơ bản.
"""
    (OUT / "BTTH02_captions.md").write_text(captions, encoding="utf-8")

    print("Generated BTTH02 assets:")
    for p in files:
        print(f"  {p}")


if __name__ == "__main__":
    main()
