from __future__ import annotations

from app.extensions import db
from app.models.auth import ActivityLog, User


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int | str) -> User | None:
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def get_by_username(username: str) -> User | None:
        return User.query.filter(db.func.lower(User.username) == username.lower()).first()

    @staticmethod
    def create(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def save(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user


class ActivityLogRepository:
    @staticmethod
    def create(log: ActivityLog) -> ActivityLog:
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def latest(limit: int = 100) -> list[ActivityLog]:
        return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
