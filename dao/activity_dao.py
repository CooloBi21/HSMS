from typing import List

from dao.data_layer import DataLayer
from models.activity import ActivityInfo


def log(action: str, detail: str) -> None:
    DataLayer.execute_non_query(
            "INSERT INTO ACTIVITY_LOG (Action, Detail) VALUES (?, ?)",
            (action, detail),
        )
    if True:
        # Giữ tối đa 50 bản ghi gần nhất
        DataLayer.execute_non_query(
            """DELETE FROM ACTIVITY_LOG WHERE id NOT IN (
                SELECT id FROM ACTIVITY_LOG ORDER BY CreatedAt DESC LIMIT 50
            )"""
        )


def get_recent(limit: int = 8, offset: int = 0) -> List[ActivityInfo]:
    rows = DataLayer.fetch_all(
        "SELECT id, CreatedAt, Action, Detail FROM ACTIVITY_LOG ORDER BY CreatedAt DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    return [
        ActivityInfo(id=r["id"], timestamp=r["CreatedAt"], action=r["Action"], detail=r["Detail"])
        for r in rows
    ]


def count_all() -> int:
    count = DataLayer.scalar("SELECT COUNT(*) AS c FROM ACTIVITY_LOG", default=0)
    return int(count or 0)
