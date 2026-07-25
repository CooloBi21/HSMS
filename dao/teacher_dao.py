from typing import List, Optional

from dao.data_layer import DataLayer
from models.teacher import GiaoVienInfo


def _row_to_info(row) -> GiaoVienInfo:
    return GiaoVienInfo(
        teacher_id=row["TeacherID"],
        teacher_code=row["TeacherCode"],
        full_name=row["FullName"],
        gender=row["Gender"],
        dob=row["DOB"],
        phone=row["Phone"],
        email=row["Email"],
        address=row["Address"],
        subject=row["Subject"],
        status=row["Status"],
    )


def get_all(search: Optional[str] = None, status: Optional[str] = None) -> List[GiaoVienInfo]:
    sql = "SELECT * FROM GIAOVIEN WHERE 1=1"
    params: list = []

    if search:
        sql += " AND (FullName LIKE ? OR TeacherCode LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])
    if status:
        sql += " AND Status = ?"
        params.append(status)

    sql += " ORDER BY FullName"
    rows = DataLayer.fetch_all(sql, params)
    return [_row_to_info(r) for r in rows]


def get_by_id(teacher_id: str) -> Optional[GiaoVienInfo]:
    row = DataLayer.fetch_one("SELECT * FROM GIAOVIEN WHERE TeacherID = ?", (teacher_id,))
    return _row_to_info(row) if row else None


def get_by_code(teacher_code: str) -> Optional[GiaoVienInfo]:
    row = DataLayer.fetch_one("SELECT * FROM GIAOVIEN WHERE TeacherCode = ?", (teacher_code,))
    return _row_to_info(row) if row else None


def insert(gv: GiaoVienInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO GIAOVIEN
           (TeacherID, TeacherCode, FullName, Gender, DOB, Phone, Email, Address, Subject, Status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            gv.teacher_id, gv.teacher_code, gv.full_name, gv.gender,
            gv.dob, gv.phone, gv.email, gv.address, gv.subject, gv.status,
        ),
    )


def update(gv: GiaoVienInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE GIAOVIEN SET TeacherCode=?, FullName=?, Gender=?, DOB=?, Phone=?,
           Email=?, Address=?, Subject=?, Status=? WHERE TeacherID=?""",
        (
            gv.teacher_code, gv.full_name, gv.gender, gv.dob, gv.phone,
            gv.email, gv.address, gv.subject, gv.status, gv.teacher_id,
        ),
    )
    return rowcount > 0


def delete(teacher_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM GIAOVIEN WHERE TeacherID = ?", (teacher_id,)) > 0


def get_max_teacher_code_num() -> int:
    """Trả về số thứ tự lớn nhất của TeacherCode dạng GV###. Dùng để sinh mã mới."""
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(TeacherCode, 3) AS INTEGER)) AS max_num "
        "FROM GIAOVIEN WHERE TeacherCode GLOB 'GV[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
