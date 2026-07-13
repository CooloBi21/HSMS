from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from config import DB_SETTINGS


class UnsupportedDatabaseProvider(ValueError):
    pass


def create_connection() -> Any:
    provider = DB_SETTINGS["provider"]
    connection_string = DB_SETTINGS["connection_string"]

    if provider == "sqlite":
        db_path = Path(connection_string)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    if provider in {"odbc", "sqlserver", "access", "oracle"}:
        try:
            import pyodbc
        except ImportError as exc:
            raise UnsupportedDatabaseProvider(
                f"Provider '{provider}' requires installing pyodbc and an appropriate ODBC database driver."
            ) from exc
        return pyodbc.connect(connection_string)

    raise UnsupportedDatabaseProvider(
        f"Unsupported database provider '{provider}'. Configure sqlite, odbc, sqlserver, access, or oracle in database_config.ini."
    )
