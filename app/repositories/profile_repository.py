from __future__ import annotations

from sqlalchemy import or_

from app.extensions import db
from app.models.academic import Student


class StudentProfileRepository:
    @staticmethod
    def list(search: str | None = None, status: str | None = None, policy_type: str | None = None) -> list[Student]:
        query = Student.query
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(Student.code.ilike(pattern), Student.full_name.ilike(pattern)))
        if status:
            query = query.filter(Student.learning_status == status)
        if policy_type:
            query = query.filter(Student.policy_type == policy_type)
        return query.order_by(Student.code).all()

    @staticmethod
    def get(student_id: int) -> Student | None:
        return db.session.get(Student, student_id)

    @staticmethod
    def learning_statuses() -> list[str]:
        rows = db.session.query(Student.learning_status).filter(Student.learning_status.isnot(None)).distinct().all()
        return sorted(row[0] for row in rows if row[0])

    @staticmethod
    def policy_types() -> list[str]:
        rows = db.session.query(Student.policy_type).filter(Student.policy_type.isnot(None)).distinct().all()
        return sorted(row[0] for row in rows if row[0])
