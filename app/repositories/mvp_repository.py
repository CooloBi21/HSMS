from __future__ import annotations

from sqlalchemy import func, or_

from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.auth import ActivityLog, User


class DashboardRepository:
    @staticmethod
    def summary() -> dict:
        return {
            "students": Student.query.count(),
            "classes": SchoolClass.query.count(),
            "teachers": Teacher.query.count(),
            "average_score": db.session.query(func.avg(Student.average_score)).scalar(),
        }

    @staticmethod
    def academic_distribution() -> list[tuple[str, int]]:
        case_expr = db.case(
            (Student.average_score >= 8.0, "Tốt"),
            (Student.average_score >= 6.5, "Khá"),
            (Student.average_score >= 5.0, "Trung bình"),
            else_="Cần theo dõi",
        )
        return db.session.query(case_expr.label("rank"), func.count(Student.id)).group_by("rank").all()

    @staticmethod
    def students_by_class() -> list[tuple[str, int]]:
        return (
            db.session.query(SchoolClass.name, func.count(Student.id))
            .outerjoin(Student, Student.class_id == SchoolClass.id)
            .group_by(SchoolClass.id, SchoolClass.name)
            .order_by(SchoolClass.code)
            .all()
        )

    @staticmethod
    def recent_activity(limit: int = 8) -> list[ActivityLog]:
        return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def data_warnings() -> list[str]:
        warnings: list[str] = []
        missing_class = Student.query.filter(Student.class_id.is_(None)).count()
        missing_score = Student.query.filter(Student.average_score.is_(None)).count()
        locked_users = User.query.filter(User.status != "active").count()
        if missing_class:
            warnings.append(f"{missing_class} học sinh chưa có lớp.")
        if missing_score:
            warnings.append(f"{missing_score} học sinh chưa có điểm trung bình.")
        if locked_users:
            warnings.append(f"{locked_users} tài khoản không hoạt động.")
        return warnings


class SchoolClassRepository:
    @staticmethod
    def list(grade_level: str | None = None) -> list[SchoolClass]:
        query = SchoolClass.query
        if grade_level:
            query = query.filter(SchoolClass.grade_level == grade_level)
        return query.order_by(SchoolClass.code).all()

    @staticmethod
    def get(class_id: int) -> SchoolClass | None:
        return db.session.get(SchoolClass, class_id)

    @staticmethod
    def get_by_code(code: str) -> SchoolClass | None:
        return SchoolClass.query.filter(func.lower(SchoolClass.code) == code.lower()).first()

    @staticmethod
    def grades() -> list[str]:
        rows = db.session.query(SchoolClass.grade_level).filter(SchoolClass.grade_level.isnot(None)).distinct().all()
        return sorted(row[0] for row in rows if row[0])


class StudentRepository:
    @staticmethod
    def list(search: str | None, class_id: int | None, page: int, per_page: int):
        query = Student.query
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(Student.code.ilike(pattern), Student.full_name.ilike(pattern)))
        if class_id:
            query = query.filter(Student.class_id == class_id)
        return query.order_by(Student.code).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get(student_id: int) -> Student | None:
        return db.session.get(Student, student_id)

    @staticmethod
    def get_by_code(code: str) -> Student | None:
        return Student.query.filter(func.lower(Student.code) == code.lower()).first()


class TeacherRepository:
    @staticmethod
    def list(status: str | None = None) -> list[Teacher]:
        query = Teacher.query
        if status:
            query = query.filter(Teacher.status == status)
        return query.order_by(Teacher.code).all()

    @staticmethod
    def get(teacher_id: int) -> Teacher | None:
        return db.session.get(Teacher, teacher_id)

    @staticmethod
    def get_by_code(code: str) -> Teacher | None:
        return Teacher.query.filter(func.lower(Teacher.code) == code.lower()).first()

    @staticmethod
    def get_by_email(email: str) -> Teacher | None:
        return Teacher.query.filter(func.lower(Teacher.email) == email.lower()).first()

    @staticmethod
    def statuses() -> list[str]:
        rows = db.session.query(Teacher.status).filter(Teacher.status.isnot(None)).distinct().all()
        return sorted(row[0] for row in rows if row[0])


class AccountRepository:
    @staticmethod
    def list() -> list[User]:
        return User.query.order_by(User.role, User.username).all()

    @staticmethod
    def get(user_id: int) -> User | None:
        return db.session.get(User, user_id)
