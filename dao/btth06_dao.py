from typing import List, Optional

from dao.data_layer import DataLayer
from models.btth06 import BusinessRecordInfo, BusinessRequirementInfo


def _row_to_requirement(row) -> BusinessRequirementInfo:
    return BusinessRequirementInfo(
        code=row["Code"],
        group_name=row["GroupName"],
        title=row["Title"],
        description=row["Description"],
        status=row["Status"],
        module_hint=row["ModuleHint"],
    )


def _row_to_record(row) -> BusinessRecordInfo:
    return BusinessRecordInfo(
        record_id=row["RecordID"],
        requirement_code=row["RequirementCode"],
        student_code=row["StudentCode"],
        title=row["Title"],
        status=row["Status"],
        event_date=row["EventDate"],
        numeric_value=row["NumericValue"],
        amount=row["Amount"],
        notes=row["Notes"],
        created_at=row["CreatedAt"],
    )


def get_requirements(
    group_name: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[BusinessRequirementInfo]:
    sql = "SELECT * FROM BTTH06_REQUIREMENT WHERE 1=1"
    params: list = []
    if group_name:
        sql += " AND GroupName = ?"
        params.append(group_name)
    if status:
        sql += " AND Status = ?"
        params.append(status)
    if search:
        sql += " AND (Code LIKE ? OR Title LIKE ? OR Description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    sql += " ORDER BY Code"
    return [_row_to_requirement(row) for row in DataLayer.fetch_all(sql, params)]


def get_requirement(code: str) -> Optional[BusinessRequirementInfo]:
    row = DataLayer.fetch_one("SELECT * FROM BTTH06_REQUIREMENT WHERE Code = ?", (code,))
    return _row_to_requirement(row) if row else None


def get_groups() -> List[str]:
    rows = DataLayer.fetch_all("SELECT DISTINCT GroupName FROM BTTH06_REQUIREMENT ORDER BY GroupName")
    return [row["GroupName"] for row in rows]


def count_requirements_by_status() -> dict:
    rows = DataLayer.fetch_all(
        "SELECT Status, COUNT(*) AS Total FROM BTTH06_REQUIREMENT GROUP BY Status"
    )
    return {row["Status"]: int(row["Total"]) for row in rows}


def get_records(
    requirement_code: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[BusinessRecordInfo]:
    sql = "SELECT * FROM BTTH06_RECORD WHERE 1=1"
    params: list = []
    if requirement_code:
        sql += " AND RequirementCode = ?"
        params.append(requirement_code)
    if status:
        sql += " AND Status = ?"
        params.append(status)
    if search:
        sql += " AND (RecordID LIKE ? OR StudentCode LIKE ? OR Title LIKE ? OR Notes LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
    sql += " ORDER BY CreatedAt DESC, RecordID DESC"
    return [_row_to_record(row) for row in DataLayer.fetch_all(sql, params)]


def get_record(record_id: str) -> Optional[BusinessRecordInfo]:
    row = DataLayer.fetch_one("SELECT * FROM BTTH06_RECORD WHERE RecordID = ?", (record_id,))
    return _row_to_record(row) if row else None


def insert_record(record: BusinessRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO BTTH06_RECORD
           (RecordID, RequirementCode, StudentCode, Title, Status, EventDate, NumericValue, Amount, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            record.record_id,
            record.requirement_code,
            record.student_code,
            record.title,
            record.status,
            record.event_date,
            record.numeric_value,
            record.amount,
            record.notes,
        ),
    )


def update_record(record: BusinessRecordInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE BTTH06_RECORD
           SET RequirementCode=?, StudentCode=?, Title=?, Status=?, EventDate=?,
               NumericValue=?, Amount=?, Notes=?
           WHERE RecordID=?""",
        (
            record.requirement_code,
            record.student_code,
            record.title,
            record.status,
            record.event_date,
            record.numeric_value,
            record.amount,
            record.notes,
            record.record_id,
        ),
    )
    return rowcount > 0


def delete_record(record_id: str) -> bool:
    return DataLayer.execute_non_query(
        "DELETE FROM BTTH06_RECORD WHERE RecordID = ?",
        (record_id,),
    ) > 0


def get_max_record_num() -> int:
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(RecordID, 2) AS INTEGER)) FROM BTTH06_RECORD WHERE RecordID GLOB 'B[0-9]*'",
        default=0,
    )
    return int(max_num or 0)


def count_records() -> int:
    return int(DataLayer.scalar("SELECT COUNT(*) FROM BTTH06_RECORD", default=0) or 0)
