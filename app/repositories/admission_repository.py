from __future__ import annotations

from sqlalchemy import func, or_

from app.extensions import db
from app.models.academic import Student
from app.models.operations import AdmissionApplication


class AdmissionRepository:
    @staticmethod
    def list(search: str | None = None, status: str | None = None) -> list[AdmissionApplication]:
        query = AdmissionApplication.query
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AdmissionApplication.application_code.ilike(pattern),
                    AdmissionApplication.full_name.ilike(pattern),
                    AdmissionApplication.phone.ilike(pattern),
                )
            )
        if status:
            query = query.filter(AdmissionApplication.status == status)
        return query.order_by(AdmissionApplication.created_at.desc(), AdmissionApplication.application_code).all()

    @staticmethod
    def get(application_id: int) -> AdmissionApplication | None:
        return db.session.get(AdmissionApplication, application_id)

    @staticmethod
    def get_by_code(application_code: str) -> AdmissionApplication | None:
        return AdmissionApplication.query.filter(
            func.lower(AdmissionApplication.application_code) == application_code.lower()
        ).first()

    @staticmethod
    def next_application_code() -> str:
        latest = (
            AdmissionApplication.query.filter(AdmissionApplication.application_code.like("TS%"))
            .order_by(AdmissionApplication.application_code.desc())
            .first()
        )
        if not latest:
            return "TS000001"
        try:
            number = int(latest.application_code[2:]) + 1
        except ValueError:
            number = AdmissionApplication.query.count() + 1
        return f"TS{number:06d}"

    @staticmethod
    def next_student_code() -> str:
        latest = Student.query.filter(Student.code.like("S%")).order_by(Student.code.desc()).first()
        if not latest:
            return "S0001"
        try:
            number = int(latest.code[1:]) + 1
        except ValueError:
            number = Student.query.count() + 1
        return f"S{number:04d}"
