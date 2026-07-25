from typing import List, Optional

from dao.data_layer import DataLayer
from models.student_affairs import (
    ConductScoreInfo,
    DormAssignmentInfo,
    ExtracurricularActivityInfo,
    HealthRecordInfo,
)


def _conduct(row) -> ConductScoreInfo:
    return ConductScoreInfo(row["ConductID"], row["MaHS"], row["Term"], row["AwarenessScore"], row["DisciplineScore"], row["ActivityScore"], row["TotalScore"], row["Rating"], row["Notes"], row["CreatedAt"])


def _dorm(row) -> DormAssignmentInfo:
    return DormAssignmentInfo(row["DormID"], row["MaHS"], row["Building"], row["Room"], row["Bed"], row["StartDate"], row["EndDate"], row["ElectricWaterFee"], row["Status"], row["Notes"])


def _activity(row) -> ExtracurricularActivityInfo:
    return ExtracurricularActivityInfo(row["ActivityID"], row["MaHS"], row["ActivityName"], row["ActivityType"], row["JoinDate"], row["Role"], row["Hours"], row["Status"], row["Notes"])


def _health(row) -> HealthRecordInfo:
    return HealthRecordInfo(row["HealthID"], row["MaHS"], row["CheckupDate"], row["HeightCm"], row["WeightKg"], row["HealthStatus"], row["InsuranceNo"], row["InsuranceExpiry"], row["Notes"])


def get_conduct_scores(ma_hs: Optional[str] = None) -> List[ConductScoreInfo]:
    sql, params = "SELECT * FROM CONDUCT_SCORE WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY Term DESC, CreatedAt DESC"
    return [_conduct(row) for row in DataLayer.fetch_all(sql, params)]


def save_conduct_score(item: ConductScoreInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO CONDUCT_SCORE
           (ConductID, MaHS, Term, AwarenessScore, DisciplineScore, ActivityScore, TotalScore, Rating, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.conduct_id, item.ma_hs, item.term, item.awareness_score, item.discipline_score, item.activity_score, item.total_score, item.rating, item.notes),
    )


def delete_conduct_score(conduct_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM CONDUCT_SCORE WHERE ConductID = ?", (conduct_id,)) > 0


def get_dorm_assignments(ma_hs: Optional[str] = None, status: Optional[str] = None) -> List[DormAssignmentInfo]:
    sql, params = "SELECT * FROM DORM_ASSIGNMENT WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    if status:
        sql += " AND Status = ?"
        params.append(status)
    sql += " ORDER BY StartDate DESC"
    return [_dorm(row) for row in DataLayer.fetch_all(sql, params)]


def save_dorm_assignment(item: DormAssignmentInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO DORM_ASSIGNMENT
           (DormID, MaHS, Building, Room, Bed, StartDate, EndDate, ElectricWaterFee, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.dorm_id, item.ma_hs, item.building, item.room, item.bed, item.start_date, item.end_date, item.electric_water_fee, item.status, item.notes),
    )


def delete_dorm_assignment(dorm_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM DORM_ASSIGNMENT WHERE DormID = ?", (dorm_id,)) > 0


def get_activities(ma_hs: Optional[str] = None) -> List[ExtracurricularActivityInfo]:
    sql, params = "SELECT * FROM EXTRACURRICULAR_ACTIVITY WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY JoinDate DESC"
    return [_activity(row) for row in DataLayer.fetch_all(sql, params)]


def save_activity(item: ExtracurricularActivityInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO EXTRACURRICULAR_ACTIVITY
           (ActivityID, MaHS, ActivityName, ActivityType, JoinDate, Role, Hours, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.activity_id, item.ma_hs, item.activity_name, item.activity_type, item.join_date, item.role, item.hours, item.status, item.notes),
    )


def delete_activity(activity_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM EXTRACURRICULAR_ACTIVITY WHERE ActivityID = ?", (activity_id,)) > 0


def get_health_records(ma_hs: Optional[str] = None) -> List[HealthRecordInfo]:
    sql, params = "SELECT * FROM HEALTH_RECORD WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY CheckupDate DESC"
    return [_health(row) for row in DataLayer.fetch_all(sql, params)]


def save_health_record(item: HealthRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO HEALTH_RECORD
           (HealthID, MaHS, CheckupDate, HeightCm, WeightKg, HealthStatus, InsuranceNo, InsuranceExpiry, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.health_id, item.ma_hs, item.checkup_date, item.height_cm, item.weight_kg, item.health_status, item.insurance_no, item.insurance_expiry, item.notes),
    )


def delete_health_record(health_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM HEALTH_RECORD WHERE HealthID = ?", (health_id,)) > 0


def get_max_num(table: str, id_column: str, prefix: str, prefix_len: int) -> int:
    max_num = DataLayer.scalar(
        f"SELECT MAX(CAST(SUBSTR({id_column}, {prefix_len + 1}) AS INTEGER)) AS max_num "
        f"FROM {table} WHERE {id_column} GLOB '{prefix}[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
