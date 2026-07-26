from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import inspect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher


REQUIRED_TARGET_TABLES = {"school_classes", "students", "teachers"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate HSMS desktop SQLite data to the configured PostgreSQL database.")
    parser.add_argument("--sqlite-path", default=os.getenv("SQLITE_DATABASE_PATH", "data/hsms.db"))
    parser.add_argument("--log-file", default=os.getenv("MIGRATION_REJECT_LOG", "backups/sqlite_to_postgres_rejects.jsonl"))
    parser.add_argument("--apply", action="store_true", help="Write records to DATABASE_URL. Default is dry-run validation only.")
    return parser.parse_args()


@contextmanager
def sqlite_connection(path: Path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


class RejectLogger:
    def __init__(self, log_file: Path) -> None:
        self.log_file = log_file
        self.rejected = 0
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.write_text("", encoding="utf-8")

    def reject(self, table: str, record: dict[str, Any], reason: str) -> None:
        self.rejected += 1
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"table": table, "record": record, "reason": reason}, ensure_ascii=False) + "\n")


def source_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        "LOP": conn.execute("SELECT COUNT(*) FROM LOP").fetchone()[0],
        "HOCSINH": conn.execute("SELECT COUNT(*) FROM HOCSINH").fetchone()[0],
        "GIAOVIEN": conn.execute("SELECT COUNT(*) FROM GIAOVIEN").fetchone()[0],
    }


def target_counts() -> dict[str, int]:
    return {
        "school_classes": SchoolClass.query.count(),
        "students": Student.query.count(),
        "teachers": Teacher.query.count(),
    }


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def select_expression(columns: set[str], column: str) -> str:
    if column in columns:
        return column
    return f"NULL AS {column}"


def validate_target_schema() -> None:
    existing = set(inspect(db.engine).get_table_names())
    missing = REQUIRED_TARGET_TABLES - existing
    if missing:
        raise RuntimeError(f"Target database is missing tables: {', '.join(sorted(missing))}. Run flask db upgrade first.")


def migrate_classes(conn: sqlite3.Connection, rejects: RejectLogger, apply: bool) -> dict[str, SchoolClass]:
    class_map: dict[str, SchoolClass] = {}
    for row in conn.execute("SELECT MaLop, TenLop, Khoi FROM LOP"):
        record = row_to_dict(row)
        if not record["MaLop"] or not record["TenLop"]:
            rejects.reject("LOP", record, "MaLop and TenLop are required.")
            continue

        school_class = SchoolClass.query.filter_by(code=record["MaLop"]).first() if apply else None
        if not school_class:
            school_class = SchoolClass(code=record["MaLop"], name=record["TenLop"], grade_level=record["Khoi"])
        else:
            school_class.name = record["TenLop"]
            school_class.grade_level = record["Khoi"]

        if apply:
            db.session.add(school_class)
            db.session.flush()
        class_map[record["MaLop"]] = school_class
    return class_map


def migrate_students(conn: sqlite3.Connection, class_map: dict[str, SchoolClass], rejects: RejectLogger, apply: bool) -> None:
    columns = table_columns(conn, "HOCSINH")
    optional_fields = ["HoKhau", "ParentName", "ParentPhone", "LearningStatus", "PolicyType"]
    select_fields = [
        "MaHS",
        "HoTen",
        "GioiTinh",
        "NgaySinh",
        "DiaChi",
        "DiemTB",
        "MaLop",
        *(select_expression(columns, field) for field in optional_fields),
    ]
    rows = conn.execute(f"SELECT {', '.join(select_fields)} FROM HOCSINH")
    for row in rows:
        record = row_to_dict(row)
        if not record["MaHS"] or not record["HoTen"]:
            rejects.reject("HOCSINH", record, "MaHS and HoTen are required.")
            continue
        if record["MaLop"] and record["MaLop"] not in class_map:
            rejects.reject("HOCSINH", record, f"Missing class foreign key: {record['MaLop']}")
            continue

        student = Student.query.filter_by(code=record["MaHS"]).first() if apply else None
        if not student:
            student = Student(code=record["MaHS"], full_name=record["HoTen"])

        student.gender = record["GioiTinh"]
        student.date_of_birth = parse_date(record["NgaySinh"])
        student.address = record["DiaChi"]
        student.average_score = record["DiemTB"]
        student.school_class = class_map.get(record["MaLop"])
        student.household = record["HoKhau"]
        student.parent_name = record["ParentName"]
        student.parent_phone = record["ParentPhone"]
        student.learning_status = record["LearningStatus"] or "Đang học"
        student.policy_type = record["PolicyType"]

        if apply:
            db.session.add(student)


def migrate_teachers(conn: sqlite3.Connection, rejects: RejectLogger, apply: bool) -> None:
    for row in conn.execute("SELECT TeacherID, TeacherCode, FullName, Gender, DOB, Phone, Email, Address, Subject, Status FROM GIAOVIEN"):
        record = row_to_dict(row)
        if not record["TeacherCode"] or not record["FullName"]:
            rejects.reject("GIAOVIEN", record, "TeacherCode and FullName are required.")
            continue

        teacher = Teacher.query.filter_by(code=record["TeacherCode"]).first() if apply else None
        if not teacher:
            teacher = Teacher(code=record["TeacherCode"], full_name=record["FullName"])

        teacher.gender = record["Gender"]
        teacher.date_of_birth = parse_date(record["DOB"])
        teacher.phone = record["Phone"]
        teacher.email = record["Email"]
        teacher.address = record["Address"]
        teacher.subject = record["Subject"]
        teacher.status = (record["Status"] or "active").lower()

        if apply:
            db.session.add(teacher)


def main() -> int:
    args = parse_args()
    sqlite_path = Path(args.sqlite_path)
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    app = create_app(os.getenv("APP_ENV") or "development")
    rejects = RejectLogger(Path(args.log_file))

    with sqlite_connection(sqlite_path) as source, app.app_context():
        before_source = source_counts(source)
        before_target = target_counts() if args.apply else {}
        print("source_counts_before", before_source)
        if args.apply:
            validate_target_schema()
            print("target_counts_before", before_target)
            db.session.rollback()
            with db.session.begin():
                class_map = migrate_classes(source, rejects, apply=True)
                migrate_students(source, class_map, rejects, apply=True)
                migrate_teachers(source, rejects, apply=True)
            after_target = target_counts()
            print("target_counts_after", after_target)
        else:
            class_map = migrate_classes(source, rejects, apply=False)
            migrate_students(source, class_map, rejects, apply=False)
            migrate_teachers(source, rejects, apply=False)
            print("dry_run", True)

    print("rejected_records", rejects.rejected)
    print("reject_log", str(rejects.log_file))
    return 0 if rejects.rejected == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
