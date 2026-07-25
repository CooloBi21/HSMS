from typing import List, Optional

from dao.data_layer import DataLayer
from models.student_decision import StudentDecisionInfo


def _row_to_info(row) -> StudentDecisionInfo:
    return StudentDecisionInfo(
        decision_id=row["DecisionID"],
        ma_hs=row["MaHS"],
        decision_type=row["DecisionType"],
        decision_date=row["DecisionDate"],
        title=row["Title"],
        description=row["Description"],
        issuer=row["Issuer"],
        created_at=row["CreatedAt"],
    )


def get_all(
    ma_hs: Optional[str] = None,
    decision_type: Optional[str] = None,
    search: Optional[str] = None,
) -> List[StudentDecisionInfo]:
    sql = "SELECT * FROM STUDENT_DECISION WHERE 1=1"
    params: list = []

    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    if decision_type:
        sql += " AND DecisionType = ?"
        params.append(decision_type)
    if search:
        sql += " AND (DecisionID LIKE ? OR MaHS LIKE ? OR Title LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    sql += " ORDER BY DecisionDate DESC, CreatedAt DESC"
    rows = DataLayer.fetch_all(sql, params)
    return [_row_to_info(row) for row in rows]


def get_by_id(decision_id: str) -> Optional[StudentDecisionInfo]:
    row = DataLayer.fetch_one(
        "SELECT * FROM STUDENT_DECISION WHERE DecisionID = ?",
        (decision_id,),
    )
    return _row_to_info(row) if row else None


def insert(decision: StudentDecisionInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO STUDENT_DECISION
           (DecisionID, MaHS, DecisionType, DecisionDate, Title, Description, Issuer)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            decision.decision_id,
            decision.ma_hs,
            decision.decision_type,
            decision.decision_date,
            decision.title,
            decision.description,
            decision.issuer,
        ),
    )


def update(decision: StudentDecisionInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE STUDENT_DECISION
           SET MaHS=?, DecisionType=?, DecisionDate=?, Title=?, Description=?, Issuer=?
           WHERE DecisionID=?""",
        (
            decision.ma_hs,
            decision.decision_type,
            decision.decision_date,
            decision.title,
            decision.description,
            decision.issuer,
            decision.decision_id,
        ),
    )
    return rowcount > 0


def delete(decision_id: str) -> bool:
    return DataLayer.execute_non_query(
        "DELETE FROM STUDENT_DECISION WHERE DecisionID = ?",
        (decision_id,),
    ) > 0


def get_max_decision_num() -> int:
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(DecisionID, 2) AS INTEGER)) AS max_num "
        "FROM STUDENT_DECISION WHERE DecisionID GLOB 'D[0-9]*'",
        default=0,
    )
    return int(max_num or 0)


def count_by_type() -> dict:
    rows = DataLayer.fetch_all(
        "SELECT DecisionType, COUNT(*) AS CountValue FROM STUDENT_DECISION GROUP BY DecisionType"
    )
    return {row["DecisionType"]: int(row["CountValue"]) for row in rows}
