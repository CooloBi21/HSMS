from typing import List, Optional

from dao.data_layer import DataLayer
from models.exam import ExamEligibilityInfo, ExamScheduleInfo, GradeRecordInfo, GradeReviewInfo


def _exam(row) -> ExamScheduleInfo:
    return ExamScheduleInfo(row["ExamID"], row["SectionID"], row["ExamDate"], row["Shift"], row["Room"], row["ExamType"])


def _eligibility(row) -> ExamEligibilityInfo:
    return ExamEligibilityInfo(
        row["EligibilityID"],
        row["ExamID"],
        row["MaHS"],
        row["CandidateNo"],
        bool(row["AttendanceEligible"]),
        bool(row["TuitionEligible"]),
        row["Status"],
        row["Notes"],
    )


def _grade(row) -> GradeRecordInfo:
    return GradeRecordInfo(
        row["GradeID"],
        row["SectionID"],
        row["MaHS"],
        row["ComponentScore"],
        row["MidtermScore"],
        row["FinalScore"],
        row["Average10"],
        row["GPA4"],
        row["LetterGrade"],
        row["UpdatedAt"],
    )


def _review(row) -> GradeReviewInfo:
    return GradeReviewInfo(
        row["ReviewID"],
        row["GradeID"],
        row["RequestDate"],
        row["Reason"],
        row["Status"],
        row["AdjustedScore"],
        row["ResolutionNotes"],
    )


def get_exams(section_id: Optional[str] = None) -> List[ExamScheduleInfo]:
    sql = "SELECT * FROM EXAM_SCHEDULE WHERE 1=1"
    params: list = []
    if section_id:
        sql += " AND SectionID = ?"
        params.append(section_id)
    sql += " ORDER BY ExamDate DESC, Shift"
    return [_exam(row) for row in DataLayer.fetch_all(sql, params)]


def get_exam(exam_id: str) -> Optional[ExamScheduleInfo]:
    row = DataLayer.fetch_one("SELECT * FROM EXAM_SCHEDULE WHERE ExamID = ?", (exam_id,))
    return _exam(row) if row else None


def insert_exam(exam: ExamScheduleInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO EXAM_SCHEDULE (ExamID, SectionID, ExamDate, Shift, Room, ExamType)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (exam.exam_id, exam.section_id, exam.exam_date, exam.shift, exam.room, exam.exam_type),
    )


def delete_exam(exam_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM EXAM_SCHEDULE WHERE ExamID = ?", (exam_id,)) > 0


def get_eligibilities(exam_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[ExamEligibilityInfo]:
    sql = "SELECT * FROM EXAM_ELIGIBILITY WHERE 1=1"
    params: list = []
    if exam_id:
        sql += " AND ExamID = ?"
        params.append(exam_id)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY CandidateNo, MaHS"
    return [_eligibility(row) for row in DataLayer.fetch_all(sql, params)]


def get_eligibility(eligibility_id: str) -> Optional[ExamEligibilityInfo]:
    row = DataLayer.fetch_one("SELECT * FROM EXAM_ELIGIBILITY WHERE EligibilityID = ?", (eligibility_id,))
    return _eligibility(row) if row else None


def insert_or_update_eligibility(item: ExamEligibilityInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO EXAM_ELIGIBILITY
           (EligibilityID, ExamID, MaHS, CandidateNo, AttendanceEligible, TuitionEligible, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item.eligibility_id,
            item.exam_id,
            item.ma_hs,
            item.candidate_no,
            1 if item.attendance_eligible else 0,
            1 if item.tuition_eligible else 0,
            item.status,
            item.notes,
        ),
    )


def delete_eligibility(eligibility_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM EXAM_ELIGIBILITY WHERE EligibilityID = ?", (eligibility_id,)) > 0


def get_grades(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[GradeRecordInfo]:
    sql = "SELECT * FROM GRADE_RECORD WHERE 1=1"
    params: list = []
    if section_id:
        sql += " AND SectionID = ?"
        params.append(section_id)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY UpdatedAt DESC"
    return [_grade(row) for row in DataLayer.fetch_all(sql, params)]


def get_grade(grade_id: str) -> Optional[GradeRecordInfo]:
    row = DataLayer.fetch_one("SELECT * FROM GRADE_RECORD WHERE GradeID = ?", (grade_id,))
    return _grade(row) if row else None


def insert_or_update_grade(grade: GradeRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO GRADE_RECORD
           (GradeID, SectionID, MaHS, ComponentScore, MidtermScore, FinalScore, Average10, GPA4, LetterGrade, UpdatedAt)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))""",
        (
            grade.grade_id,
            grade.section_id,
            grade.ma_hs,
            grade.component_score,
            grade.midterm_score,
            grade.final_score,
            grade.average10,
            grade.gpa4,
            grade.letter_grade,
        ),
    )


def delete_grade(grade_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM GRADE_RECORD WHERE GradeID = ?", (grade_id,)) > 0


def get_reviews(status: Optional[str] = None) -> List[GradeReviewInfo]:
    sql = "SELECT * FROM GRADE_REVIEW WHERE 1=1"
    params: list = []
    if status:
        sql += " AND Status = ?"
        params.append(status)
    sql += " ORDER BY RequestDate DESC"
    return [_review(row) for row in DataLayer.fetch_all(sql, params)]


def get_review(review_id: str) -> Optional[GradeReviewInfo]:
    row = DataLayer.fetch_one("SELECT * FROM GRADE_REVIEW WHERE ReviewID = ?", (review_id,))
    return _review(row) if row else None


def insert_or_update_review(review: GradeReviewInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO GRADE_REVIEW
           (ReviewID, GradeID, RequestDate, Reason, Status, AdjustedScore, ResolutionNotes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            review.review_id,
            review.grade_id,
            review.request_date,
            review.reason,
            review.status,
            review.adjusted_score,
            review.resolution_notes,
        ),
    )


def delete_review(review_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM GRADE_REVIEW WHERE ReviewID = ?", (review_id,)) > 0


def get_max_num(table: str, id_column: str, prefix: str, prefix_len: int) -> int:
    max_num = DataLayer.scalar(
        f"SELECT MAX(CAST(SUBSTR({id_column}, {prefix_len + 1}) AS INTEGER)) AS max_num "
        f"FROM {table} WHERE {id_column} GLOB '{prefix}[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
