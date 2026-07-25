from typing import List, Optional

from dao import teacher_dao, student_dao, school_class_dao, training_dao
from models.training import (
    AttendanceRecordInfo,
    ClassScheduleInfo,
    CourseInfo,
    CourseRegistrationInfo,
    CourseSectionInfo,
    CurriculumItemInfo,
)
from services import activity_service

SECTION_STATUSES = ("Mở đăng ký", "Đang học", "Kết thúc", "Tạm dừng")
REGISTRATION_STATUSES = ("Đăng ký", "Đã hủy")
ATTENDANCE_STATUSES = ("Có mặt", "Vắng", "Đi muộn", "Có phép")
WEEKDAYS = ("Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật")


def list_courses(search: Optional[str] = None) -> List[CourseInfo]:
    return training_dao.get_courses(search=search)


def list_curriculum(grade_level: Optional[str] = None) -> List[CurriculumItemInfo]:
    return training_dao.get_curriculum_items(grade_level=grade_level)


def list_sections(status: Optional[str] = None) -> List[CourseSectionInfo]:
    return training_dao.get_sections(status=status)


def list_registrations(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[CourseRegistrationInfo]:
    return training_dao.get_registrations(section_id=section_id, ma_hs=ma_hs)


def list_schedules(section_id: Optional[str] = None) -> List[ClassScheduleInfo]:
    return training_dao.get_schedules(section_id=section_id)


def list_attendance(section_id: Optional[str] = None, ma_hs: Optional[str] = None) -> List[AttendanceRecordInfo]:
    return training_dao.get_attendance(section_id=section_id, ma_hs=ma_hs)


def summary() -> dict:
    attendance = list_attendance()
    absent = len([a for a in attendance if a.status in ("Vắng", "Đi muộn")])
    return {
        "courses": len(list_courses()),
        "sections": len(list_sections()),
        "registrations": len(list_registrations()),
        "attendance_issues": absent,
    }


def next_course_id() -> str:
    return f"MH{training_dao.get_max_num('COURSE', 'CourseID', 'MH', 2) + 1:03d}"


def next_curriculum_id() -> str:
    return f"CT{training_dao.get_max_num('CURRICULUM_ITEM', 'ItemID', 'CT', 2) + 1:04d}"


def next_section_id() -> str:
    return f"HP{training_dao.get_max_num('COURSE_SECTION', 'SectionID', 'HP', 2) + 1:04d}"


def next_registration_id() -> str:
    return f"DK{training_dao.get_max_num('COURSE_REGISTRATION', 'RegistrationID', 'DK', 2) + 1:04d}"


def next_schedule_id() -> str:
    return f"TKB{training_dao.get_max_num('CLASS_SCHEDULE', 'ScheduleID', 'TKB', 3) + 1:04d}"


def next_attendance_id() -> str:
    return f"DD{training_dao.get_max_num('ATTENDANCE_RECORD', 'AttendanceID', 'DD', 2) + 1:05d}"


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def create_course(course: CourseInfo) -> CourseInfo:
    course.course_id = course.course_id.strip()
    course.course_name = course.course_name.strip()
    course.grade_level = _normalize_optional(course.grade_level)
    course.prerequisite_id = _normalize_optional(course.prerequisite_id)
    course.description = _normalize_optional(course.description)
    if not course.course_id:
        raise ValueError("Mã môn học không được để trống.")
    if not course.course_name:
        raise ValueError("Tên môn học không được để trống.")
    if course.credits <= 0:
        raise ValueError("Số tín chỉ phải lớn hơn 0.")
    if course.prerequisite_id and not training_dao.get_course(course.prerequisite_id):
        raise ValueError("Môn tiên quyết không tồn tại.")
    if training_dao.get_course(course.course_id):
        raise ValueError(f"Mã môn học '{course.course_id}' đã tồn tại.")
    training_dao.insert_course(course)
    activity_service.log_activity("Thêm môn học", f"Thêm môn học {course.course_name}")
    return course


def create_curriculum_item(item: CurriculumItemInfo) -> CurriculumItemInfo:
    item.item_id = item.item_id.strip()
    item.course_id = item.course_id.strip()
    item.grade_level = item.grade_level.strip()
    item.semester = item.semester.strip()
    item.notes = _normalize_optional(item.notes)
    if not training_dao.get_course(item.course_id):
        raise ValueError("Môn học trong khung chương trình không tồn tại.")
    if not item.grade_level or not item.semester:
        raise ValueError("Khối/khóa và học kỳ không được để trống.")
    if training_dao.get_curriculum_item(item.item_id):
        raise ValueError(f"Mã dòng khung chương trình '{item.item_id}' đã tồn tại.")
    training_dao.insert_curriculum_item(item)
    activity_service.log_activity("Thêm khung chương trình", f"Thêm {item.course_id} vao {item.grade_level} - {item.semester}")
    return item


def create_section(section: CourseSectionInfo) -> CourseSectionInfo:
    section.section_id = section.section_id.strip()
    section.course_id = section.course_id.strip()
    section.class_code = _normalize_optional(section.class_code)
    section.teacher_id = _normalize_optional(section.teacher_id)
    section.status = section.status or "Mở đăng ký"
    if not training_dao.get_course(section.course_id):
        raise ValueError("Môn học không tồn tại.")
    if section.class_code and not school_class_dao.get_by_id(section.class_code):
        raise ValueError("Lớp sinh hoạt không tồn tại.")
    if section.teacher_id and not teacher_dao.get_by_id(section.teacher_id):
        raise ValueError("Giáo viên không tồn tại.")
    if section.capacity is not None and section.capacity <= 0:
        raise ValueError("Sĩ số tối đa phải lớn hơn 0.")
    if section.status not in SECTION_STATUSES:
        raise ValueError("Trạng thái lop học phần không hợp lệ.")
    if training_dao.get_section(section.section_id):
        raise ValueError(f"Mã lớp học phần '{section.section_id}' đã tồn tại.")
    training_dao.insert_section(section)
    activity_service.log_activity("Mã lớp học phần", f"Mã lớp học phần {section.section_id}")
    return section


def register_student(reg: CourseRegistrationInfo) -> CourseRegistrationInfo:
    reg.registration_id = reg.registration_id.strip()
    reg.section_id = reg.section_id.strip()
    reg.ma_hs = reg.ma_hs.strip()
    reg.status = reg.status or "Đăng ký"
    section = training_dao.get_section(reg.section_id)
    if not section:
        raise ValueError("Lớp học phần không tồn tại.")
    if not student_dao.get_by_id(reg.ma_hs):
        raise ValueError("Học sinh không tồn tại.")
    if reg.status not in REGISTRATION_STATUSES:
        raise ValueError("Trạng thái đăng ký không hợp lệ.")
    if any(r.ma_hs == reg.ma_hs for r in training_dao.get_registrations(section_id=reg.section_id)):
        raise ValueError("Học sinh đã đăng ký lớp học phần này.")
    if section.capacity is not None and len(training_dao.get_registrations(section_id=reg.section_id)) >= section.capacity:
        raise ValueError("Lớp học phần đã đủ sĩ số.")
    training_dao.insert_registration(reg)
    activity_service.log_activity("Đăng ký học phần", f"{reg.ma_hs} đăng ký {reg.section_id}")
    return reg


def create_schedule(schedule: ClassScheduleInfo) -> ClassScheduleInfo:
    schedule.schedule_id = schedule.schedule_id.strip()
    schedule.section_id = schedule.section_id.strip()
    schedule.room = schedule.room.strip()
    if schedule.weekday not in WEEKDAYS:
        raise ValueError("Thứ trong tuần không hợp lệ.")
    if schedule.start_period <= 0 or schedule.end_period < schedule.start_period:
        raise ValueError("Tiết học không hợp lệ.")
    section = training_dao.get_section(schedule.section_id)
    if not section:
        raise ValueError("Lớp học phần không tồn tại.")
    _check_schedule_conflict(schedule, section)
    training_dao.insert_schedule(schedule)
    activity_service.log_activity("Xep thoi khoa bieu", f"Xep {schedule.section_id} tai phòng {schedule.room}")
    return schedule


def record_attendance(att: AttendanceRecordInfo) -> AttendanceRecordInfo:
    att.attendance_id = att.attendance_id.strip()
    att.section_id = att.section_id.strip()
    att.ma_hs = att.ma_hs.strip()
    att.attendance_date = att.attendance_date.strip()
    att.notes = _normalize_optional(att.notes)
    if att.status not in ATTENDANCE_STATUSES:
        raise ValueError("Trạng thái Điểm danh không hợp lệ.")
    if not any(r.ma_hs == att.ma_hs for r in training_dao.get_registrations(section_id=att.section_id)):
        raise ValueError("Học sinh chưa đăng ký lớp học phần này.")
    if not att.attendance_date:
        raise ValueError("Ngày Điểm danh không được để trống.")
    training_dao.insert_or_update_attendance(att)
    activity_service.log_activity("Điểm danh", f"{att.ma_hs} - {att.section_id}: {att.status}")
    return att


def delete_course(course_id: str) -> bool:
    return training_dao.delete_course(course_id)


def delete_curriculum_item(item_id: str) -> bool:
    return training_dao.delete_curriculum_item(item_id)


def delete_section(section_id: str) -> bool:
    return training_dao.delete_section(section_id)


def delete_registration(registration_id: str) -> bool:
    return training_dao.delete_registration(registration_id)


def delete_schedule(schedule_id: str) -> bool:
    return training_dao.delete_schedule(schedule_id)


def delete_attendance(attendance_id: str) -> bool:
    return training_dao.delete_attendance(attendance_id)


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start <= b_end and b_start <= a_end


def _check_schedule_conflict(schedule: ClassScheduleInfo, section: CourseSectionInfo) -> None:
    for existing in training_dao.get_schedules():
        if existing.weekday != schedule.weekday:
            continue
        if not _overlap(schedule.start_period, schedule.end_period, existing.start_period, existing.end_period):
            continue
        existing_section = training_dao.get_section(existing.section_id)
        if not existing_section:
            continue
        if existing.room == schedule.room:
            raise ValueError("Trung phòng hoc trong cung thoi gian.")
        if section.teacher_id and existing_section.teacher_id == section.teacher_id:
            raise ValueError("Giáo viên bị trùng lịch dạy.")
        if section.class_code and existing_section.class_code == section.class_code:
            raise ValueError("Lớp sinh hoạt bị trùng lịch học.")
