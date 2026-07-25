from typing import List, Optional

from dao.data_layer import DataLayer
from models.graduation import AlumniEmploymentInfo, DiplomaRecordInfo, DocumentRequestInfo, GraduationCheckInfo


def _check(row) -> GraduationCheckInfo:
    return GraduationCheckInfo(row["CheckID"], row["MaHS"], row["CheckDate"], row["RequiredCredits"], row["EarnedCredits"], bool(row["InformaticsCert"]), bool(row["LanguageCert"]), bool(row["DefenseCert"]), row["Status"], row["Notes"])


def _diploma(row) -> DiplomaRecordInfo:
    return DiplomaRecordInfo(row["DiplomaID"], row["MaHS"], row["RegistryNo"], row["DiplomaNo"], row["IssueDate"], row["Status"], row["GraduationCheckID"], row["Notes"])


def _document(row) -> DocumentRequestInfo:
    return DocumentRequestInfo(row["RequestID"], row["MaHS"], row["DocumentType"], row["RequestDate"], row["Status"], row["OutputPath"], row["Notes"])


def _alumni(row) -> AlumniEmploymentInfo:
    return AlumniEmploymentInfo(row["AlumniID"], row["MaHS"], row["SurveyDate"], row["EmploymentStatus"], row["Company"], row["Position"], row["Salary"], row["Notes"])


def get_checks(ma_hs: Optional[str] = None) -> List[GraduationCheckInfo]:
    sql, params = "SELECT * FROM GRADUATION_CHECK WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY CheckDate DESC"
    return [_check(row) for row in DataLayer.fetch_all(sql, params)]


def get_check(check_id: str) -> Optional[GraduationCheckInfo]:
    row = DataLayer.fetch_one("SELECT * FROM GRADUATION_CHECK WHERE CheckID = ?", (check_id,))
    return _check(row) if row else None


def save_check(item: GraduationCheckInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO GRADUATION_CHECK
           (CheckID, MaHS, CheckDate, RequiredCredits, EarnedCredits, InformaticsCert, LanguageCert, DefenseCert, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.check_id, item.ma_hs, item.check_date, item.required_credits, item.earned_credits, int(item.informatics_cert), int(item.language_cert), int(item.defense_cert), item.status, item.notes),
    )


def delete_check(check_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM GRADUATION_CHECK WHERE CheckID = ?", (check_id,)) > 0


def get_diplomas(ma_hs: Optional[str] = None) -> List[DiplomaRecordInfo]:
    sql, params = "SELECT * FROM DIPLOMA_RECORD WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY IssueDate DESC"
    return [_diploma(row) for row in DataLayer.fetch_all(sql, params)]


def save_diploma(item: DiplomaRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO DIPLOMA_RECORD
           (DiplomaID, MaHS, GraduationCheckID, RegistryNo, DiplomaNo, IssueDate, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.diploma_id, item.ma_hs, item.graduation_check_id, item.registry_no, item.diploma_no, item.issue_date, item.status, item.notes),
    )


def delete_diploma(diploma_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM DIPLOMA_RECORD WHERE DiplomaID = ?", (diploma_id,)) > 0


def get_documents(ma_hs: Optional[str] = None) -> List[DocumentRequestInfo]:
    sql, params = "SELECT * FROM DOCUMENT_REQUEST WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY RequestDate DESC"
    return [_document(row) for row in DataLayer.fetch_all(sql, params)]


def save_document(item: DocumentRequestInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO DOCUMENT_REQUEST
           (RequestID, MaHS, DocumentType, RequestDate, Status, OutputPath, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (item.request_id, item.ma_hs, item.document_type, item.request_date, item.status, item.output_path, item.notes),
    )


def delete_document(request_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM DOCUMENT_REQUEST WHERE RequestID = ?", (request_id,)) > 0


def get_alumni(ma_hs: Optional[str] = None) -> List[AlumniEmploymentInfo]:
    sql, params = "SELECT * FROM ALUMNI_EMPLOYMENT WHERE 1=1", []
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY SurveyDate DESC"
    return [_alumni(row) for row in DataLayer.fetch_all(sql, params)]


def save_alumni(item: AlumniEmploymentInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO ALUMNI_EMPLOYMENT
           (AlumniID, MaHS, SurveyDate, EmploymentStatus, Company, Position, Salary, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (item.alumni_id, item.ma_hs, item.survey_date, item.employment_status, item.company, item.position, item.salary, item.notes),
    )


def delete_alumni(alumni_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM ALUMNI_EMPLOYMENT WHERE AlumniID = ?", (alumni_id,)) > 0


def get_max_num(table: str, id_column: str, prefix: str, prefix_len: int) -> int:
    max_num = DataLayer.scalar(
        f"SELECT MAX(CAST(SUBSTR({id_column}, {prefix_len + 1}) AS INTEGER)) AS max_num "
        f"FROM {table} WHERE {id_column} GLOB '{prefix}[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
