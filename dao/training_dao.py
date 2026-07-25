from typing import List, Optional

from dao.data_layer import DataLayer
from models.training import (
    AttendanceRecordInfo,
    ClassScheduleInfo,
    CourseInfo,
    CourseRegistrationInfo,
    CourseSectionInfo,
    CurriculumItemInfo,
)


def _course(row) -> CourseInfo:
    return CourseInfo(row["CourseID"], row["CourseName"], row["Credits"], row["GradeLevel"], row["PrerequisiteID"], row["Description"])


def _curriculum(row) -> CurriculumItemInfo:
    return CurriculumItemInfo(row["ItemID"], row["CourseID"], row["GradeLevel"], row["Semester"], row["SequenceNo"], row["Notes"])


def _section(row) -> CourseSectionInfo:
    return CourseSectionInfo(row["SectionID"], row["CourseID"], row["ClassCode"], row["TeacherID"], row["Capacity"], row["Status"])


def _registration(row) -> CourseRegistrationInfo:
    return CourseRegistrationInfo(row["RegistrationID"], row["SectionID"], row["MaHS"], row["Status"], row["RegisteredAt"])


def _schedule(row) -> ClassScheduleInfo:
    return ClassScheduleInfo(row["ScheduleID"], row["SectionID"], row["Weekday"], row["StartPeriod"], row["EndPeriod"], row["Room"])


def _attendance(row) -> AttendanceRecordInfo:
    return AttendanceRecordInfo(row["AttendanceID"], row["SectionID"], row["MaHS"], row["AttendanceDate"], row["Status"], row["Notes"])


def get_courses(search: Optional[str] = None) -> List[CourseInfo]:
    sql = "SELECT * FROM COURSE WHERE 1=1"
    params: list = []
    if search:
        sql += " AND (CourseID LIKE ? OR CourseName LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])
    sql += " ORDER BY GradeLevel, CourseName"
    return [_course(row) for row in DataLayer.fetch_all(sql, params)]


def get_course(course_id: str) -> Optional[CourseInfo]:
    row = DataLayer.fetch_one("SELECT * FROM COURSE WHERE CourseID = ?", (course_id,))
    return _course(row) if row else None


def insert_course(course: CourseInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO COURSE (CourseID, CourseName, Credits, GradeLevel, PrerequisiteID, Description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (course.course_id, course.course_name, course.credits, course.grade_level, course.prerequisite_id, course.description),
    )


def update_course(course: CourseInfo) -> bool:
    return DataLayer.execute_non_query(
        """UPDATE COURSE SET CourseName=?, Credits=?, GradeLevel=?, PrerequisiteID=?, Description=?
           WHERE CourseID=?""",
        (course.course_name, course.credits, course.grade_level, course.prerequisite_id, course.description, course.course_id),
    ) > 0


def delete_course(course_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM COURSE WHERE CourseID = ?", (course_id,)) > 0


def get_curriculum_items(grade_level: Optional[str] = None) -> List[CurriculumItemInfo]:
    sql = "SELECT * FROM CURRICULUM_ITEM WHERE 1=1"
    params: list = []
    if grade_level:
        sql += " AND GradeLevel = ?"
        params.append(grade_level)
    sql += " ORDER BY GradeLevel, Semester, SequenceNo"
    return [_curriculum(row) for row in DataLayer.fetch_all(sql, params)]


def get_curriculum_item(item_id: str) -> Optional[CurriculumItemInfo]:
    row = DataLayer.fetch_one("SELECT * FROM CURRICULUM_ITEM WHERE ItemID = ?", (item_id,))
    return _curriculum(row) if row else None


def insert_curriculum_item(item: CurriculumItemInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO CURRICULUM_ITEM (ItemID, CourseID, GradeLevel, Semester, SequenceNo, Notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (item.item_id, item.course_id, item.grade_level, item.semester, item.sequence_no, item.notes),
    )


def delete_curriculum_item(item_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM CURRICULUM_ITEM WHERE ItemID = ?", (item_id,)) > 0


def get_sections(status: Optional[str] = None) -> List[CourseSectionInfo]:
    sql = "SELECT * FROM COURSE_SECTION WHERE 1=1"
    params: list = []
    if status:
        sql += " AND Status = ?"
        params.append(status)
    sql += " ORDER BY SectionID DESC"
    return [_section(row) for row in DataLayer.fetch_all(sql, params)]


def get_section(section_id: str) -> Optional[CourseSectionInfo]:
    row = DataLayer.fetch_one("SELECT * FROM COURSE_SECTION WHERE SectionID = ?", (section_id,))
    return _section(row) if row else None


def insert_section(section: CourseSectionInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO COURSE_SECTION (SectionID, CourseID, ClassCode, TeacherID, Capacity, Status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (section.section_id, section.course_id, section.class_code, section.teacher_id, section.capacity, section.status),
    )


def update_section(section: CourseSectionInfo) -> bool:
    return DataLayer.execute_non_query(
        """UPDATE COURSE_SECTION SET CourseID=?, ClassCode=?, TeacherID=?, Capacity=?, Status=?
           WHERE SectionID=?""",
        (section.course_id, section.class_code, section.teacher_id, section.capacity, section.status, section.section_id),
    ) > 0


def delete_section(section_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM COURSE_SECTION WHERE SectionID = ?", (section_id,)) > 0


def get_registrations(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[CourseRegistrationInfo]:
    sql = "SELECT * FROM COURSE_REGISTRATION WHERE 1=1"
    params: list = []
    if section_id:
        sql += " AND SectionID = ?"
        params.append(section_id)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY RegisteredAt DESC"
    return [_registration(row) for row in DataLayer.fetch_all(sql, params)]


def get_registration(registration_id: str) -> Optional[CourseRegistrationInfo]:
    row = DataLayer.fetch_one("SELECT * FROM COURSE_REGISTRATION WHERE RegistrationID = ?", (registration_id,))
    return _registration(row) if row else None


def insert_registration(reg: CourseRegistrationInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO COURSE_REGISTRATION (RegistrationID, SectionID, MaHS, Status)
           VALUES (?, ?, ?, ?)""",
        (reg.registration_id, reg.section_id, reg.ma_hs, reg.status),
    )


def delete_registration(registration_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM COURSE_REGISTRATION WHERE RegistrationID = ?", (registration_id,)) > 0


def get_schedules(section_id: Optional[str] = None) -> List[ClassScheduleInfo]:
    sql = "SELECT * FROM CLASS_SCHEDULE WHERE 1=1"
    params: list = []
    if section_id:
        sql += " AND SectionID = ?"
        params.append(section_id)
    sql += " ORDER BY Weekday, StartPeriod"
    return [_schedule(row) for row in DataLayer.fetch_all(sql, params)]


def get_schedule(schedule_id: str) -> Optional[ClassScheduleInfo]:
    row = DataLayer.fetch_one("SELECT * FROM CLASS_SCHEDULE WHERE ScheduleID = ?", (schedule_id,))
    return _schedule(row) if row else None


def insert_schedule(schedule: ClassScheduleInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO CLASS_SCHEDULE (ScheduleID, SectionID, Weekday, StartPeriod, EndPeriod, Room)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (schedule.schedule_id, schedule.section_id, schedule.weekday, schedule.start_period, schedule.end_period, schedule.room),
    )


def delete_schedule(schedule_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM CLASS_SCHEDULE WHERE ScheduleID = ?", (schedule_id,)) > 0


def get_attendance(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[AttendanceRecordInfo]:
    sql = "SELECT * FROM ATTENDANCE_RECORD WHERE 1=1"
    params: list = []
    if section_id:
        sql += " AND SectionID = ?"
        params.append(section_id)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY AttendanceDate DESC"
    return [_attendance(row) for row in DataLayer.fetch_all(sql, params)]


def insert_or_update_attendance(att: AttendanceRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO ATTENDANCE_RECORD
           (AttendanceID, SectionID, MaHS, AttendanceDate, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (att.attendance_id, att.section_id, att.ma_hs, att.attendance_date, att.status, att.notes),
    )


def delete_attendance(attendance_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM ATTENDANCE_RECORD WHERE AttendanceID = ?", (attendance_id,)) > 0


def get_max_num(table: str, id_column: str, prefix: str, prefix_len: int) -> int:
    max_num = DataLayer.scalar(
        f"SELECT MAX(CAST(SUBSTR({id_column}, {prefix_len + 1}) AS INTEGER)) AS max_num "
        f"FROM {table} WHERE {id_column} GLOB '{prefix}[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
