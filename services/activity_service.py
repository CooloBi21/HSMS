from typing import List

from dao import activity_dao
from models.activity import ActivityInfo


def log_activity(action: str, detail: str) -> None:
    activity_dao.log(action, detail)


def get_recent_activities(limit: int = 5, offset: int = 0) -> List[ActivityInfo]:
    return activity_dao.get_recent(limit=limit, offset=offset)


def count_activities() -> int:
    return activity_dao.count_all()
