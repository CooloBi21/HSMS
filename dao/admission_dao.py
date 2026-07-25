from typing import List, Optional

from dao.data_layer import DataLayer
from models.admission import AdmissionApplicationInfo


def _row_to_info(row) -> AdmissionApplicationInfo:
    return AdmissionApplicationInfo(
        application_id=row["ApplicationID"],
        full_name=row["FullName"],
        gender=row["Gender"],
        dob=row["DOB"],
        address=row["Address"],
        phone=row["Phone"],
        parent_name=row["ParentName"],
        parent_phone=row["ParentPhone"],
        admission_score=row["AdmissionScore"],
        desired_class=row["DesiredClass"],
        desired_major=row["DesiredMajor"],
        status=row["Status"],
        student_code=row["StudentCode"],
        notes=row["Notes"],
        created_at=row["CreatedAt"],
        updated_at=row["UpdatedAt"],
    )


def get_all(status: Optional[str] = None, search: Optional[str] = None) -> List[AdmissionApplicationInfo]:
    sql = "SELECT * FROM ADMISSION_APPLICATION WHERE 1=1"
    params: list = []

    if status:
        sql += " AND Status = ?"
        params.append(status)
    if search:
        sql += " AND (ApplicationID LIKE ? OR FullName LIKE ? OR Phone LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    sql += " ORDER BY CreatedAt DESC, ApplicationID DESC"
    rows = DataLayer.fetch_all(sql, params)
    return [_row_to_info(row) for row in rows]


def get_by_id(application_id: str) -> Optional[AdmissionApplicationInfo]:
    row = DataLayer.fetch_one(
        "SELECT * FROM ADMISSION_APPLICATION WHERE ApplicationID = ?",
        (application_id,),
    )
    return _row_to_info(row) if row else None


def insert(app: AdmissionApplicationInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO ADMISSION_APPLICATION
           (ApplicationID, FullName, Gender, DOB, Address, Phone, ParentName, ParentPhone,
            AdmissionScore, DesiredClass, DesiredMajor, Status, StudentCode, Notes, UpdatedAt)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))""",
        (
            app.application_id,
            app.full_name,
            app.gender,
            app.dob,
            app.address,
            app.phone,
            app.parent_name,
            app.parent_phone,
            app.admission_score,
            app.desired_class,
            app.desired_major,
            app.status,
            app.student_code,
            app.notes,
        ),
    )


def update(app: AdmissionApplicationInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE ADMISSION_APPLICATION
           SET FullName=?, Gender=?, DOB=?, Address=?, Phone=?, ParentName=?, ParentPhone=?,
               AdmissionScore=?, DesiredClass=?, DesiredMajor=?, Status=?, StudentCode=?,
               Notes=?, UpdatedAt=datetime('now', 'localtime')
           WHERE ApplicationID=?""",
        (
            app.full_name,
            app.gender,
            app.dob,
            app.address,
            app.phone,
            app.parent_name,
            app.parent_phone,
            app.admission_score,
            app.desired_class,
            app.desired_major,
            app.status,
            app.student_code,
            app.notes,
            app.application_id,
        ),
    )
    return rowcount > 0


def delete(application_id: str) -> bool:
    return DataLayer.execute_non_query(
        "DELETE FROM ADMISSION_APPLICATION WHERE ApplicationID = ?",
        (application_id,),
    ) > 0


def get_max_application_num() -> int:
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(ApplicationID, 2) AS INTEGER)) AS max_num "
        "FROM ADMISSION_APPLICATION WHERE ApplicationID GLOB 'A[0-9]*'",
        default=0,
    )
    return int(max_num or 0)


def count_by_status() -> dict:
    rows = DataLayer.fetch_all(
        "SELECT Status, COUNT(*) AS CountValue FROM ADMISSION_APPLICATION GROUP BY Status"
    )
    return {row["Status"]: int(row["CountValue"]) for row in rows}
