from pathlib import Path
import configparser

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "hsms.db"
INIT_SQL = BASE_DIR / "database" / "init_db.sql"
DATABASE_CONFIG = BASE_DIR / "database_config.ini"

APP_TITLE = "HSMS — Quản lý Học sinh"
APP_SIZE = "1280x800"
MIN_SIZE = (1100, 680)


def _load_database_settings() -> dict:
    parser = configparser.ConfigParser()
    parser.read(DATABASE_CONFIG, encoding="utf-8")

    section = parser["database"] if parser.has_section("database") else {}
    provider = section.get("provider", "sqlite").strip().lower()
    connection_string = section.get("connection_string", str(DB_FILE)).strip()

    if provider == "sqlite":
        db_path = Path(connection_string)
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path
        connection_string = str(db_path)

    return {
        "provider": provider,
        "connection_string": connection_string,
    }


DB_SETTINGS = _load_database_settings()
