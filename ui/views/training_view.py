import customtkinter as ctk
from tkinter import messagebox

from models.training import (
    AttendanceRecordInfo,
    ClassScheduleInfo,
    CourseInfo,
    CourseRegistrationInfo,
    CourseSectionInfo,
    CurriculumItemInfo,
)
from services import teacher_service, student_service, school_class_service, training_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class TrainingView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._courses: dict = {}
        self._sections: dict = {}
        self._students: dict = {}
        self._classes: dict = {}
        self._teachers: dict = {}
        self._metrics: dict = {}
        self._build()

    def _build(self) -> None:
        heading(self, "Đào tạo & Xếp lịch", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Quản lý môn học, khung chương trình, đăng ký học phần, lịch học và điểm danh.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("courses", "Môn học", "#2563eb", "Khung CT", "MH"),
                ("sections", "Học phần", "#10b981", "Đang mo", "HP"),
                ("registrations", "Đăng ký", "#7c3aed", "Học sinh", "DK"),
                ("attendance_issues", "Vắng/trễ", "#ef4444", "Cần theo dõi", "!"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        self._course_tab = tabs.add("Khung CT")
        self._section_tab = tabs.add("Học phần")
        self._schedule_tab = tabs.add("TKB")
        self._attendance_tab = tabs.add("Điểm danh")
        self._build_course_tab()
        self._build_section_tab()
        self._build_schedule_tab()
        self._build_attendance_tab()

        if self._on_navigate:
            ScreenNavBar(self, "training", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _build_course_tab(self) -> None:
        self._course_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._course_tab.grid_columnconfigure(1, weight=1)
        self._course_tab.grid_rowconfigure(0, weight=1)
        self._course_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._course_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)

        self._course_id = self._entry(form, "Mã môn học", training_service.next_course_id())
        self._course_name = self._entry(form, "Tên môn học")
        self._credits = self._entry(form, "Số tín chỉ", "3")
        self._grade_level = self._entry(form, "Khối/Khóa", "10")
        self._prerequisite = self._combo(form, "Môn tiên quyết", ["Không"])
        self._course_desc = self._entry(form, "Mô tả")
        ctk.CTkButton(form, text="Thêm môn học", command=self._save_course, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)

        self._curriculum_id = self._entry(form, "Mã dòng khung CT", training_service.next_curriculum_id())
        self._curriculum_course = self._combo(form, "Môn trong khung", ["Chọn môn"])
        self._curriculum_semester = self._entry(form, "Học kỳ", "HK1")
        self._curriculum_seq = self._entry(form, "Thứ tự", "1")
        ctk.CTkButton(form, text="Thêm vào khung CT", command=self._save_curriculum, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa môn học đang chọn", command=self._delete_selected_course, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._course_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._course_table = DataTable(
            table_area,
            columns=[("id", "Mã", 80), ("name", "Môn học", 170), ("credits", "TC", 55), ("grade", "Khối", 70), ("pre", "Tiền quyet", 90)],
        )
        self._course_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_section_tab(self) -> None:
        self._section_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._section_tab.grid_columnconfigure(1, weight=1)
        self._section_tab.grid_rowconfigure(0, weight=1)
        self._section_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._section_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)

        self._section_id = self._entry(form, "Mã học phần", training_service.next_section_id())
        self._section_course = self._combo(form, "Môn học", ["Chọn môn"])
        self._section_class = self._combo(form, "Lớp sinh hoạt", ["Không"])
        self._section_teacher = self._combo(form, "Giáo viên", ["Không"])
        self._section_capacity = self._entry(form, "Sĩ số tối đa", "40")
        ctk.CTkButton(form, text="Mã lớp học phần", command=self._save_section, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)

        self._registration_id = self._entry(form, "Mở đăng ký", training_service.next_registration_id())
        self._registration_section = self._combo(form, "Học phần", ["Chọn học phần"])
        self._registration_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        ctk.CTkButton(form, text="Đăng ký học phần", command=self._save_registration, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa học phần đang chọn", command=self._delete_selected_section, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._section_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._section_table = DataTable(
            table_area,
            columns=[("id", "Mã HP", 80), ("course", "Môn", 100), ("class", "Lớp", 80), ("teacher", "GV", 100), ("cap", "Sĩ số", 65), ("regs", "DK", 55)],
        )
        self._section_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_schedule_tab(self) -> None:
        self._schedule_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._schedule_tab.grid_columnconfigure(1, weight=1)
        self._schedule_tab.grid_rowconfigure(0, weight=1)
        self._schedule_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._schedule_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)

        self._schedule_id = self._entry(form, "Mã lịch học", training_service.next_schedule_id())
        self._schedule_section = self._combo(form, "Học phần", ["Chọn học phần"])
        self._weekday = self._combo(form, "Thứ", list(training_service.WEEKDAYS))
        self._start_period = self._entry(form, "Tiết bắt đầu", "1")
        self._end_period = self._entry(form, "Tiết kết thức", "3")
        self._room = self._entry(form, "Phòng học", "P101")
        ctk.CTkButton(form, text="Xếp lịch học", command=self._save_schedule, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa lịch học đang chọn", command=self._delete_selected_schedule, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._schedule_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._schedule_table = DataTable(
            table_area,
            columns=[("id", "Mã", 85), ("section", "HP", 85), ("day", "Thứ", 80), ("period", "Tiết", 80), ("room", "Phòng", 90)],
        )
        self._schedule_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_attendance_tab(self) -> None:
        self._attendance_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._attendance_tab.grid_columnconfigure(1, weight=1)
        self._attendance_tab.grid_rowconfigure(0, weight=1)
        self._attendance_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._attendance_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)

        self._attendance_id = self._entry(form, "Mã Điểm danh", training_service.next_attendance_id())
        self._attendance_section = self._combo(form, "Học phần", ["Chọn học phần"])
        self._attendance_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._attendance_date = self._entry(form, "Ngày Điểm danh", "2026-07-21")
        self._attendance_status = self._combo(form, "Trạng thái", list(training_service.ATTENDANCE_STATUSES))
        self._attendance_notes = self._entry(form, "Ghi chỉ")
        ctk.CTkButton(form, text="Lưu điểm danh", command=self._save_attendance, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa điểm danh đang chọn", command=self._delete_selected_attendance, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._attendance_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._attendance_table = DataTable(
            table_area,
            columns=[("id", "Mã", 85), ("section", "HP", 85), ("student", "HS", 80), ("date", "Ngày", 100), ("status", "Trạng thái", 100)],
        )
        self._attendance_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _entry(self, parent, label: str, value: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=36)
        entry.insert(0, value)
        entry.pack(fill="x", padx=12, pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=36)
        if values:
            combo.set(values[0])
        combo.pack(fill="x", padx=12, pady=(2, 0))
        return combo

    def _code_from_label(self, mapping: dict, label: str) -> str | None:
        return mapping.get(label)

    def _set_entry_value(self, entry, value: str) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)

    def _refresh_options(self) -> None:
        courses = training_service.list_courses()
        self._courses = {f"{c.course_name} ({c.course_id})": c.course_id for c in courses}
        course_values = ["Chọn môn"] + list(self._courses.keys())
        prereq_values = ["Không"] + list(self._courses.keys())
        for combo in (self._curriculum_course, self._section_course):
            combo.configure(values=course_values)
            if combo.get() not in course_values:
                combo.set(course_values[0])
        self._prerequisite.configure(values=prereq_values)
        if self._prerequisite.get() not in prereq_values:
            self._prerequisite.set("Không")

        sections = training_service.list_sections()
        self._sections = {f"{s.section_id} - {s.course_id}": s.section_id for s in sections}
        section_values = ["Chọn học phần"] + list(self._sections.keys())
        for combo in (self._registration_section, self._schedule_section, self._attendance_section):
            combo.configure(values=section_values)
            if combo.get() not in section_values:
                combo.set(section_values[0])

        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        student_values = ["Chọn học sinh"] + list(self._students.keys())
        for combo in (self._registration_student, self._attendance_student):
            combo.configure(values=student_values)
            if combo.get() not in student_values:
                combo.set(student_values[0])

        classes = school_class_service.list_classes()
        self._classes = {f"{c.ten_lop} ({c.ma_lop})": c.ma_lop for c in classes}
        class_values = ["Không"] + list(self._classes.keys())
        self._section_class.configure(values=class_values)

        teachers = teacher_service.list_teachers(status="Active")
        self._teachers = {f"{t.full_name} ({t.teacher_id})": t.teacher_id for t in teachers}
        teacher_values = ["Không"] + list(self._teachers.keys())
        self._section_teacher.configure(values=teacher_values)

    def _save_course(self) -> None:
        try:
            course = CourseInfo(
                course_id=self._course_id.get().strip(),
                course_name=self._course_name.get().strip(),
                credits=int(self._credits.get().strip()),
                grade_level=self._grade_level.get().strip() or None,
                prerequisite_id=self._code_from_label(self._courses, self._prerequisite.get()),
                description=self._course_desc.get().strip() or None,
            )
            training_service.create_course(course)
            messagebox.showinfo("Thành công", "Đã thêm môn học.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_curriculum(self) -> None:
        try:
            item = CurriculumItemInfo(
                item_id=self._curriculum_id.get().strip(),
                course_id=self._code_from_label(self._courses, self._curriculum_course.get()) or "",
                grade_level=self._grade_level.get().strip() or "10",
                semester=self._curriculum_semester.get().strip(),
                sequence_no=int(self._curriculum_seq.get().strip() or 0),
            )
            training_service.create_curriculum_item(item)
            messagebox.showinfo("Thành công", "Đã thêm môn vào khung chương trình.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_section(self) -> None:
        try:
            section = CourseSectionInfo(
                section_id=self._section_id.get().strip(),
                course_id=self._code_from_label(self._courses, self._section_course.get()) or "",
                class_code=self._code_from_label(self._classes, self._section_class.get()),
                teacher_id=self._code_from_label(self._teachers, self._section_teacher.get()),
                capacity=int(self._section_capacity.get().strip() or 0),
            )
            training_service.create_section(section)
            messagebox.showinfo("Thành công", "Đã mở lớp học phần.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_registration(self) -> None:
        try:
            reg = CourseRegistrationInfo(
                registration_id=self._registration_id.get().strip(),
                section_id=self._code_from_label(self._sections, self._registration_section.get()) or "",
                ma_hs=self._code_from_label(self._students, self._registration_student.get()) or "",
            )
            training_service.register_student(reg)
            messagebox.showinfo("Thành công", "Đã đăng kỳ học phần.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_schedule(self) -> None:
        try:
            schedule = ClassScheduleInfo(
                schedule_id=self._schedule_id.get().strip(),
                section_id=self._code_from_label(self._sections, self._schedule_section.get()) or "",
                weekday=self._weekday.get().strip(),
                start_period=int(self._start_period.get().strip()),
                end_period=int(self._end_period.get().strip()),
                room=self._room.get().strip(),
            )
            training_service.create_schedule(schedule)
            messagebox.showinfo("Thành công", "Đã xếp lịch học.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_attendance(self) -> None:
        try:
            att = AttendanceRecordInfo(
                attendance_id=self._attendance_id.get().strip(),
                section_id=self._code_from_label(self._sections, self._attendance_section.get()) or "",
                ma_hs=self._code_from_label(self._students, self._attendance_student.get()) or "",
                attendance_date=self._attendance_date.get().strip(),
                status=self._attendance_status.get().strip(),
                notes=self._attendance_notes.get().strip() or None,
            )
            training_service.record_attendance(att)
            messagebox.showinfo("Thành công", "Đã lưu Điểm danh.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))


    def _selected_table_id(self, table, empty_message: str):
        values = table.get_selected_values()
        if not values:
            messagebox.showwarning("Cảnh báo", empty_message)
            return None
        return values[0]

    def _delete_selected_course(self):
        values = self._course_table.get_selected_values()
        if values:
            self._course_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học cần xóa.")

    def _delete_selected_section(self):
        values = self._section_table.get_selected_values()
        if values:
            self._section_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn học phần cần xóa.")

    def _delete_selected_schedule(self):
        values = self._schedule_table.get_selected_values()
        if values:
            self._schedule_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch học cần xóa.")

    def _delete_selected_attendance(self):
        values = self._attendance_table.get_selected_values()
        if values:
            self._attendance_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn điểm danh cần xóa.")

    def _course_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa môn {values[0]}?"):
            training_service.delete_course(values[0])
            self.refresh()

    def _section_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa học phần {values[0]}?"):
            training_service.delete_section(values[0])
            self.refresh()

    def _schedule_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa lịch {values[0]}?"):
            training_service.delete_schedule(values[0])
            self.refresh()

    def _attendance_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa Điểm danh {values[0]}?"):
            training_service.delete_attendance(values[0])
            self.refresh()

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _render_tables(self) -> None:
        courses = training_service.list_courses()
        self._course_table.load([(c.course_id, c.course_name, c.credits, c.grade_level or "", c.prerequisite_id or "", "Xóa") for c in courses])

        registrations = training_service.list_registrations()
        reg_counts = {}
        for reg in registrations:
            reg_counts[reg.section_id] = reg_counts.get(reg.section_id, 0) + 1
        sections = training_service.list_sections()
        self._section_table.load([(s.section_id, s.course_id, s.class_code or "", s.teacher_id or "", s.capacity or "", reg_counts.get(s.section_id, 0), "Xóa") for s in sections])

        schedules = training_service.list_schedules()
        self._schedule_table.load([(s.schedule_id, s.section_id, s.weekday, f"{s.start_period}-{s.end_period}", s.room, "Xóa") for s in schedules])

        attendance = training_service.list_attendance()
        self._attendance_table.load([(a.attendance_id, a.section_id, a.ma_hs, a.attendance_date, a.status, "Xóa") for a in attendance])

    def refresh(self) -> None:
        self._refresh_options()
        summary = training_service.summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))
        self._render_tables()
        self._set_entry_value(self._course_id, training_service.next_course_id())
        self._set_entry_value(self._curriculum_id, training_service.next_curriculum_id())
        self._set_entry_value(self._section_id, training_service.next_section_id())
        self._set_entry_value(self._registration_id, training_service.next_registration_id())
        self._set_entry_value(self._schedule_id, training_service.next_schedule_id())
        self._set_entry_value(self._attendance_id, training_service.next_attendance_id())
