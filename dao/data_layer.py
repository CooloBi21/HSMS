from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from typing import Any, TypeVar

from dao.db_provider import create_connection

T = TypeVar("T")


def _row_to_dict(row: Any, columns: Sequence[str] | None = None) -> dict:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    if isinstance(row, dict):
        return row
    if columns:
        return {column: value for column, value in zip(columns, row)}
    return dict(row)


class DataLayer:
    """Lop dung chung cho DAO: query va execute non-query tren provider hien tai."""

    @staticmethod
    def execute_non_query(sql: str, params: Iterable[Any] = ()) -> int:
        conn = create_connection()
        try:
            cur = conn.execute(sql, tuple(params))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    @staticmethod
    def fetch_all(sql: str, params: Iterable[Any] = ()) -> list[dict]:
        conn = create_connection()
        try:
            cur = conn.execute(sql, tuple(params))
            rows = cur.fetchall()
            columns = [column[0] for column in cur.description] if cur.description else None
            return [_row_to_dict(row, columns) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def fetch_one(sql: str, params: Iterable[Any] = ()) -> dict | None:
        rows = DataLayer.fetch_all(sql, params)
        return rows[0] if rows else None

    @staticmethod
    def scalar(sql: str, params: Iterable[Any] = (), default: T | None = None) -> Any | T | None:
        row = DataLayer.fetch_one(sql, params)
        if not row:
            return default
        return next(iter(row.values()))
