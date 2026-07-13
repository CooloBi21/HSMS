from pathlib import Path

from config import DATA_DIR, DB_SETTINGS, INIT_SQL
from dao.db_provider import create_connection


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    return create_connection()


def init_database() -> None:
    if DB_SETTINGS["provider"] != "sqlite":
        return

    _ensure_data_dir()
    if not INIT_SQL.exists():
        raise FileNotFoundError(f"Missing init script: {INIT_SQL}")

    sql = INIT_SQL.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(sql)
        conn.commit()


def init_database_if_needed() -> None:
    if DB_SETTINGS["provider"] != "sqlite":
        return

    _ensure_data_dir()
    db_file = Path(DB_SETTINGS["connection_string"])
    if not db_file.exists():
        init_database()
    else:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='HOCSINH'"
            ).fetchone()
            if not row:
                init_database()
    _ensure_migrations()


def _ensure_migrations() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
                Action TEXT NOT NULL,
                Detail TEXT NOT NULL
            )
        """)
        conn.commit()
        # Xóa dữ liệu demo cũ (seed tĩnh) nếu còn
        conn.execute("""
            DELETE FROM ACTIVITY_LOG WHERE Detail IN (
                'Thêm học sinh Nguyễn Văn An vào lớp 10A1',
                'Nhập điểm TB cho lớp 10A1',
                'Cập nhật thông tin lớp 11B2',
                'Thêm giáo viên Lê Thị Hương — môn Toán'
            )
        """)
        conn.commit()
