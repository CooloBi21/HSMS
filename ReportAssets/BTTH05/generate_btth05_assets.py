from __future__ import annotations

import subprocess
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageGrab


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

BG = "#f5f7fb"
INK = "#172033"
MUTED = "#5b667a"
CARD = "#ffffff"
BORDER = "#dbe3ef"
BLUE = "#2563eb"
GREEN = "#059669"
AMBER = "#d97706"
PURPLE = "#7c3aed"
RED = "#dc2626"
TEAL = "#0f766e"


def font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


FONT_TITLE = font("C:/Windows/Fonts/segoeuib.ttf", 38)
FONT_HEAD = font("C:/Windows/Fonts/segoeuib.ttf", 30)
FONT_UI = font("C:/Windows/Fonts/segoeui.ttf", 24)
FONT_SMALL = font("C:/Windows/Fonts/segoeui.ttf", 21)
FONT_MONO = font("C:/Windows/Fonts/consola.ttf", 20)
FONT_MONO_SMALL = font("C:/Windows/Fonts/consola.ttf", 18)
FONT_MONO_TINY = font("C:/Windows/Fonts/consola.ttf", 16)
FONT_MONO_MICRO = font("C:/Windows/Fonts/consola.ttf", 14)


CAPTIONS: list[tuple[str, str]] = []


def read_lines(relative: str) -> list[str]:
    return (ROOT / relative).read_text(encoding="utf-8").splitlines()


def extract_between(relative: str, start_marker: str, end_marker: str | None = None, max_lines: int = 80) -> tuple[int, list[str]]:
    lines = read_lines(relative)
    start = next((i for i, line in enumerate(lines) if start_marker in line), 0)
    end = min(len(lines), start + max_lines)
    if end_marker:
        for i in range(start + 1, min(len(lines), start + max_lines)):
            if end_marker in lines[i]:
                end = i
                break
    return start + 1, lines[start:end]


def wrap(text: str, width: int) -> list[str]:
    out: list[str] = []
    for paragraph in text.split("\n"):
        out.extend(textwrap.wrap(paragraph, width=width) or [""])
    return out


def add_caption(filename: str, caption: str) -> None:
    CAPTIONS.append((filename, caption))


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj) -> int:
    return draw.textbbox((0, 0), text, font=font_obj)[2]


def wrap_to_width(draw: ImageDraw.ImageDraw, text: str, font_obj, max_width: int) -> list[str]:
    if not text:
        return [""]
    if text_width(draw, text, font_obj) <= max_width:
        return [text]

    chunks: list[str] = []
    remaining = text
    continuation_indent = "    "
    first_line = True

    while remaining:
        prefix = "" if first_line else continuation_indent
        available = max_width - text_width(draw, prefix, font_obj)
        low = 1
        high = len(remaining)
        best = 1
        while low <= high:
            mid = (low + high) // 2
            candidate = remaining[:mid]
            if text_width(draw, candidate, font_obj) <= available:
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        split_at = best
        if best < len(remaining):
            whitespace = max(remaining.rfind(" ", 0, best), remaining.rfind(",", 0, best), remaining.rfind(")", 0, best))
            if whitespace > max(1, best // 2):
                split_at = whitespace + 1

        chunks.append(prefix + remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
        first_line = False

    return chunks


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, accent: str) -> None:
    draw.rounded_rectangle((44, 34, 1556, 148), radius=18, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((44, 34, 62, 148), fill=accent)
    draw.text((92, 52), title, font=FONT_TITLE, fill=INK)
    draw.text((92, 105), subtitle, font=FONT_SMALL, fill=MUTED)


def draw_code_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    lines: list[str],
    start_line: int,
    accent: str,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x2, y1 + 52), fill="#eef4ff")
    draw.rectangle((x1, y1, x1 + 12, y2), fill=accent)
    draw.text((x1 + 28, y1 + 13), label, font=FONT_SMALL, fill=INK)
    y = y1 + 74
    panel_width = x2 - x1
    if panel_width < 520:
        code_font = FONT_MONO_MICRO
        line_font = FONT_MONO_MICRO
        line_height = 19
    elif panel_width < 620:
        code_font = FONT_MONO_TINY
        line_font = FONT_MONO_TINY
        line_height = 22
    else:
        code_font = FONT_MONO
        line_font = FONT_MONO_SMALL
        line_height = 25
    text_x = x1 + 76
    text_max_width = x2 - text_x - 18
    for idx, line in enumerate(lines):
        compact = line.expandtabs(4)
        visual_lines = wrap_to_width(draw, compact, code_font, text_max_width)
        for visual_idx, visual_line in enumerate(visual_lines):
            if y > y2 - 24:
                return
            line_number = f"{start_line + idx:>3}" if visual_idx == 0 else "   "
            draw.text((x1 + 24, y), line_number, font=line_font, fill="#95a3b8")
            draw.text((text_x, y), visual_line, font=code_font, fill=INK)
            y += line_height


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, body: str, accent: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill=CARD, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 12, y2), fill=accent)
    draw.text((x1 + 34, y1 + 24), title, font=FONT_HEAD, fill=INK)
    y = y1 + 76
    for line in wrap(body, max(24, int((x2 - x1 - 70) / 11))):
        draw.text((x1 + 34, y), line, font=FONT_UI, fill=MUTED)
        y += 32


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    draw.line((start, end), fill="#64748b", width=5)
    x, y = end
    draw.polygon([(x, y), (x - 15, y - 9), (x - 15, y + 9)], fill="#64748b")


def save_flow_image() -> None:
    filename = "BTTH05_01_architecture_requirement_flow.png"
    img = Image.new("RGB", (1600, 920), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - Yeu cau kien truc linh hoat",
        "Tom tat dung y PDF: tach cau hinh ket noi, tao lop dung chung, DAO tai su dung va de doi DBMS.",
        BLUE,
    )
    boxes = [
        ("File cau hinh", "Thong tin ket noi nam ngoai code trong database_config.ini.", BLUE),
        ("Provider", "db_provider tao connection theo provider hien tai: sqlite, sqlserver, access, oracle hoac odbc.", TEAL),
        ("DataLayer", "Cac ham query/non-query dung chung cho nhieu DAO.", GREEN),
        ("DAO cu the", "Hoc sinh, lop, giao vien, activity giu API cu nhung goi DataLayer.", AMBER),
    ]
    xs = [70, 455, 840, 1225]
    for i, (title, body, color) in enumerate(boxes):
        draw_box(draw, (xs[i], 305, xs[i] + 305, 565), title, body, color)
        if i < len(boxes) - 1:
            draw_arrow(draw, (xs[i] + 320, 435), (xs[i + 1] - 18, 435))
    add_caption(
        filename,
        "Hinh 1. So do yeu cau BTTH05: thong tin ket noi duoc dua ra file cau hinh, provider tao connection, DataLayer gom logic query/non-query va cac DAO tai su dung lai lop dung chung.",
    )
    img.save(OUT / filename)


def save_config_image() -> None:
    filename = "BTTH05_02_external_database_config.png"
    config_start, config_lines = 1, read_lines("database_config.ini")
    py_start, py_lines = extract_between("config.py", "DATABASE_CONFIG", "DB_SETTINGS", 36)
    img = Image.new("RGB", (1600, 1200), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - Cau hinh ket noi nam ngoai code",
        "Minh chung co the doi provider/connection_string trong file cau hinh ma khong sua DAO hay service.",
        PURPLE,
    )
    draw_code_panel(draw, (60, 190, 780, 1130), "database_config.ini", config_lines, config_start, PURPLE)
    draw_code_panel(draw, (820, 190, 1540, 1130), "config.py doc database_config.ini", py_lines, py_start, BLUE)
    add_caption(
        filename,
        "Hinh 2. File database_config.ini luu provider va connection_string ben ngoai ma nguon; config.py doc file nay de tao DB_SETTINGS cho toan bo tang du lieu.",
    )
    img.save(OUT / filename)


def save_provider_image() -> None:
    filename = "BTTH05_03_database_provider_factory.png"
    start, lines = extract_between("dao/db_provider.py", "def create_connection", None, 45)
    img = Image.new("RGB", (1600, 1100), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - Factory tao ket noi theo provider",
        "Lop nay la diem thay doi DBMS: sqlite ho tro truc tiep; SQL Server, Access, Oracle di qua ODBC/pyodbc.",
        TEAL,
    )
    draw_code_panel(draw, (70, 185, 1530, 1030), "dao/db_provider.py", lines, start, TEAL)
    add_caption(
        filename,
        "Hinh 3. db_provider.py tao connection theo provider trong cau hinh, giup chuong trinh co diem mo rong khi chuyen sang SQL Server, Access hoac Oracle qua ODBC.",
    )
    img.save(OUT / filename)


def save_datalayer_image() -> None:
    filename = "BTTH05_04_reusable_data_layer.png"
    start, lines = extract_between("dao/data_layer.py", "class DataLayer", None, 40)
    img = Image.new("RGB", (1600, 1120), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - DataLayer dung chung cho DAO",
        "Thay vi moi DAO tu mo connection va commit, DataLayer gom execute_non_query, fetch_all, fetch_one va scalar.",
        GREEN,
    )
    draw_code_panel(draw, (70, 185, 1530, 1050), "dao/data_layer.py", lines, start, GREEN)
    add_caption(
        filename,
        "Hinh 4. DataLayer gom cac thao tac truy cap du lieu lap lai: execute_non_query cho them/sua/xoa, fetch_all/fetch_one cho truy van va scalar cho gia tri don.",
    )
    img.save(OUT / filename)


def save_dao_refactor_image() -> None:
    filename = "BTTH05_05_dao_reuse_datalayer.png"
    hs_start, hs_lines = extract_between("dao/hoc_sinh_dao.py", "def insert", "def count_by_class", 45)
    lop_start, lop_lines = extract_between("dao/lop_dao.py", "def insert", "def get_max_ma_lop_num", 34)
    gv_start, gv_lines = extract_between("dao/giao_vien_dao.py", "def insert", "def get_max_teacher_code_num", 45)
    img = Image.new("RGB", (1600, 1280), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - Cac DAO tai su dung DataLayer",
        "Hoc sinh, lop va giao vien khong lap lai logic connection/commit; API cu van giu de service va UI khong doi.",
        AMBER,
    )
    draw_code_panel(draw, (55, 185, 520, 1210), "hoc_sinh_dao.py", hs_lines, hs_start, BLUE)
    draw_code_panel(draw, (565, 185, 1030, 1210), "lop_dao.py", lop_lines, lop_start, GREEN)
    draw_code_panel(draw, (1075, 185, 1540, 1210), "giao_vien_dao.py", gv_lines, gv_start, AMBER)
    add_caption(
        filename,
        "Hinh 5. Cac DAO cu the da chuyen sang goi DataLayer cho insert, update, delete va query; service/UI van dung cac ham DAO cu nen khong lam thay doi nghiep vu hien co.",
    )
    img.save(OUT / filename)


def run_check() -> str:
    code = (
        "from dao.db import init_database_if_needed; "
        "init_database_if_needed(); "
        "from services import hoc_sinh_service, lop_service, giao_vien_service, activity_service; "
        "from dao.data_layer import DataLayer; "
        "print('BTTH05 runtime check'); "
        "print('students', len(hoc_sinh_service.list_students())); "
        "print('classes', len(lop_service.list_classes())); "
        "print('teachers', len(giao_vien_service.list_teachers())); "
        "print('activities', activity_service.count_activities()); "
        "print('DataLayer HOCSINH count', DataLayer.scalar('SELECT COUNT(*) FROM HOCSINH'))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return output or f"command exited with code {result.returncode}"


def save_runtime_check_image() -> None:
    filename = "BTTH05_06_runtime_data_access_check.png"
    output = run_check().splitlines()
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    draw_header(
        draw,
        "BTTH05 - Chay kiem tra tang du lieu sau refactor",
        "Ket qua doc du lieu qua service va DataLayer sau khi doi sang kien truc cau hinh/provider/DataLayer.",
        RED,
    )
    draw_box(
        draw,
        (70, 190, 1530, 330),
        "Lenh kiem tra",
        "Khoi tao database neu can, goi service hoc sinh/lop/giao vien/activity va dem truc tiep bang DataLayer.",
        RED,
    )
    draw_code_panel(draw, (70, 365, 1530, 810), "Ket qua console", output, 1, RED)
    add_caption(
        filename,
        "Hinh 6. Ket qua chay kiem tra: service van doc duoc du lieu hoc sinh, lop, giao vien va activity; DataLayer truy van truc tiep duoc bang HOCSINH.",
    )
    img.save(OUT / filename)


def save_app_screenshot() -> None:
    filename = "BTTH05_07_running_app_dashboard_after_datalayer.png"
    try:
        from dao.db import init_database_if_needed
        from ui.app import HSMSApp

        init_database_if_needed()
        app = HSMSApp()
        app.geometry("1360x760+40+20")
        app.minsize(1200, 720)
        app.update_idletasks()
        app.update()
        time.sleep(0.8)
        app.update_idletasks()
        app.update()
        if hasattr(app, "_show_view"):
            app._show_view("dashboard")
            app.update_idletasks()
            app.update()
            time.sleep(0.5)
        x = app.winfo_rootx()
        y = app.winfo_rooty()
        w = app.winfo_width()
        h = app.winfo_height()
        image = ImageGrab.grab((x, y, x + w, y + h))
        image.save(OUT / filename)
        app.destroy()
        add_caption(
            filename,
            "Hinh 7. Phan mem HSMS chay duoc sau BTTH05; dashboard lay du lieu thong qua service/DAO da refactor sang DataLayer.",
        )
    except Exception as exc:
        img = Image.new("RGB", (1600, 900), BG)
        draw = ImageDraw.Draw(img)
        draw_header(draw, "BTTH05 - Khong chup duoc GUI", "Moi truong hien tai khong cho phep ImageGrab hoac hien thi cua so ung dung.", RED)
        draw_code_panel(draw, (70, 220, 1530, 780), "Loi chup GUI", [repr(exc)], 1, RED)
        img.save(OUT / filename)
        add_caption(
            filename,
            "Hinh 7. Anh ghi nhan viec moi truong khong cho phep chup GUI; cac ket qua chay tang du lieu duoc the hien o Hinh 6.",
        )


def write_captions() -> None:
    lines = ["# Chu thich hinh BTTH05 - Kien truc tai su dung va cau hinh CSDL", ""]
    lines.append("| File | Chu thich |")
    lines.append("|------|-----------|")
    for filename, caption in CAPTIONS:
        lines.append(f"| `{filename}` | {caption} |")
    (OUT / "BTTH05_captions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    save_flow_image()
    save_config_image()
    save_provider_image()
    save_datalayer_image()
    save_dao_refactor_image()
    save_runtime_check_image()
    save_app_screenshot()
    write_captions()


if __name__ == "__main__":
    main()
