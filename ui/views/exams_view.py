import customtkinter as ctk
from tkinter import messagebox

from models.exam import ExamScheduleInfo, GradeRecordInfo, GradeReviewInfo
from services import exam_service, student_service, training_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class ExamsView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._sections: dict = {}
        self._students: dict = {}
        self._grades: dict = {}
        self._metrics: dict = {}
        self._build()

    def _build(self) -> None:
        heading(self, "Khảo thí & Điểm số", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Lập lịch thi, đánh số báo danh, nhập điểm, tính GPA, xét điều kiện và phúc khảo.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("exams", "Lịch thi", "#2563eb", "Đã lập", "EX"),
                ("grades", "Bảng Điểm", "#10b981", "Đã nhập", "GR"),
                ("locked", "Bị khóa thi", "#ef4444", "Không đủ điều kiện", "!"),
                ("reviews", "Phúc khảo", "#7c3aed", "Yêu cầu", "PK"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        self._exam_tab = tabs.add("Lịch thi")
        self._grade_tab = tabs.add("Điểm")
        self._review_tab = tabs.add("Phúc khảo")
        self._build_exam_tab()
        self._build_grade_tab()
        self._build_review_tab()

        if self._on_navigate:
            ScreenNavBar(self, "exams", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _build_exam_tab(self) -> None:
        self._exam_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._exam_tab.grid_columnconfigure(1, weight=1)
        self._exam_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._exam_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._exam_id = self._entry(form, "Mã lịch thi", exam_service.next_exam_id())
        self._exam_section = self._combo(form, "Học phần", ["Chọn học phần"])
        self._exam_date = self._entry(form, "Ngày thi", "2026-07-21")
        self._exam_shift = self._entry(form, "Ca thi", "Ca 1")
        self._exam_room = self._entry(form, "Phòng thi", "PTH01")
        self._exam_type = self._combo(form, "Loại thi", list(exam_service.EXAM_TYPES))
        ctk.CTkButton(form, text="Lập lịch thi", command=self._save_exam, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Đánh số báo danh & xét điều kiện", command=self._generate_eligibility, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa lịch thi đang chọn", command=self._delete_selected_exam, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa điều kiện thi đang chọn", command=self._delete_selected_eligibility, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._exam_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._exam_table = DataTable(
            table_area,
            columns=[("id", "Mã", 80), ("section", "HP", 90), ("date", "Ngày", 100), ("shift", "Ca", 80), ("room", "Phòng", 80), ("type", "Loại", 90)],
            on_select=self._on_exam_select,
        )
        self._exam_table.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        self._eligibility_table = DataTable(
            table_area,
            columns=[("id", "Mã", 110), ("exam", "Lịch", 80), ("student", "HS", 80), ("no", "SBD", 60), ("status", "Trạng thái", 120), ("notes", "Ghi chú", 150)],
        )
        self._eligibility_table.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    def _build_grade_tab(self) -> None:
        self._grade_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._grade_tab.grid_columnconfigure(1, weight=1)
        self._grade_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._grade_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._grade_id = self._entry(form, "Mã bằng Điểm", exam_service.next_grade_id())
        self._grade_section = self._combo(form, "Học phần", ["Chọn học phần"])
        self._grade_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._component_score = self._entry(form, "Điểm thành phần", "8")
        self._midterm_score = self._entry(form, "Điểm giữa kỳ", "8")
        self._final_score = self._entry(form, "Điểm cuối kỳ", "8")
        ctk.CTkButton(form, text="Lưu điểm & tính GPA", command=self._save_grade, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa bảng điểm đang chọn", command=self._delete_selected_grade, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._grade_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._grade_table = DataTable(
            table_area,
            columns=[("id", "Mã", 80), ("section", "HP", 90), ("student", "HS", 80), ("cc", "TP", 60), ("mid", "GK", 60), ("final", "CK", 60), ("avg", "TB10", 70), ("gpa", "GPA4", 70), ("letter", "XL", 55)],
        )
        self._grade_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_review_tab(self) -> None:
        self._review_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._review_tab.grid_columnconfigure(1, weight=1)
        self._review_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._review_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._review_id = self._entry(form, "Mã phúc khảo", exam_service.next_review_id())
        self._review_grade = self._combo(form, "Bảng điểm", ["Chọn bảng điểm"])
        self._review_date = self._entry(form, "Ngày yêu cầu", "2026-07-21")
        self._review_reason = self._entry(form, "Lý do")
        self._review_status = self._combo(form, "Trạng thái", list(exam_service.REVIEW_STATUSES))
        self._adjusted_score = self._entry(form, "Điểm điều chỉnh nếu có")
        self._review_notes = self._entry(form, "Kết quả xử lý")
        ctk.CTkButton(form, text="Lưu phúc khảo", command=self._save_review, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa phúc khảo đang chọn", command=self._delete_selected_review, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._review_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._review_table = DataTable(
            table_area,
            columns=[("id", "Mã", 85), ("grade", "Bảng điểm", 90), ("date", "Ngày", 100), ("status", "Trạng thái", 110), ("score", "Điểm mới", 80), ("reason", "Lý do", 180)],
        )
        self._review_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _entry(self, parent, label: str, value: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=36)
        entry.insert(0, value)
        entry.pack(fill="x", padx=12, pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=36)
        combo.set(values[0])
        combo.pack(fill="x", padx=12, pady=(2, 0))
        return combo

    def _set_entry(self, entry, value: str) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)

    def _code(self, mapping: dict, label: str) -> str | None:
        return mapping.get(label)

    def _parse_score(self, entry) -> float | None:
        value = entry.get().strip()
        return float(value) if value else None

    def _refresh_options(self) -> None:
        sections = training_service.list_sections()
        self._sections = {f"{s.section_id} - {s.course_id}": s.section_id for s in sections}
        section_values = ["Chọn học phần"] + list(self._sections.keys())
        for combo in (self._exam_section, self._grade_section):
            combo.configure(values=section_values)
            if combo.get() not in section_values:
                combo.set(section_values[0])

        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        student_values = ["Chọn học sinh"] + list(self._students.keys())
        self._grade_student.configure(values=student_values)
        if self._grade_student.get() not in student_values:
            self._grade_student.set(student_values[0])

        grades = exam_service.list_grades()
        self._grades = {f"{g.grade_id} - {g.ma_hs}": g.grade_id for g in grades}
        grade_values = ["Chọn bằng Điểm"] + list(self._grades.keys())
        self._review_grade.configure(values=grade_values)
        if self._review_grade.get() not in grade_values:
            self._review_grade.set(grade_values[0])

    def _save_exam(self) -> None:
        try:
            exam = ExamScheduleInfo(
                self._exam_id.get().strip(),
                self._code(self._sections, self._exam_section.get()) or "",
                self._exam_date.get().strip(),
                self._exam_shift.get().strip(),
                self._exam_room.get().strip(),
                self._exam_type.get().strip(),
            )
            exam_service.create_exam(exam)
            messagebox.showinfo("Thành công", "Đã lập lịch thi.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _generate_eligibility(self) -> None:
        exam_id = self._exam_id.get().strip()
        try:
            count = exam_service.generate_eligibility_for_exam(exam_id)
            messagebox.showinfo("Thành công", f"Đã xét điều kiện cho {count} học sinh.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_grade(self) -> None:
        try:
            grade = GradeRecordInfo(
                self._grade_id.get().strip(),
                self._code(self._sections, self._grade_section.get()) or "",
                self._code(self._students, self._grade_student.get()) or "",
                self._parse_score(self._component_score),
                self._parse_score(self._midterm_score),
                self._parse_score(self._final_score),
            )
            exam_service.save_grade(grade)
            messagebox.showinfo("Thành công", "Đã lưu điểm và tính GPA.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_review(self) -> None:
        try:
            review = GradeReviewInfo(
                self._review_id.get().strip(),
                self._code(self._grades, self._review_grade.get()) or "",
                self._review_date.get().strip(),
                self._review_reason.get().strip(),
                self._review_status.get().strip(),
                self._parse_score(self._adjusted_score),
                self._review_notes.get().strip() or None,
            )
            exam_service.submit_review(review)
            messagebox.showinfo("Thành công", "Đã lưu yêu cầu phúc khảo.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))


    def _delete_selected_exam(self):
        values = self._exam_table.get_selected_values()
        if values:
            self._exam_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch thi cần xóa.")

    def _delete_selected_eligibility(self):
        values = self._eligibility_table.get_selected_values()
        if values:
            self._eligibility_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn điều kiện thi cần xóa.")

    def _delete_selected_grade(self):
        values = self._grade_table.get_selected_values()
        if values:
            self._grade_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bảng điểm cần xóa.")

    def _delete_selected_review(self):
        values = self._review_table.get_selected_values()
        if values:
            self._review_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phúc khảo cần xóa.")

    def _on_exam_select(self, values: tuple) -> None:
        if values:
            self._set_entry(self._exam_id, values[0])
            self._eligibility_table.load([
                (e.eligibility_id, e.exam_id, e.ma_hs, e.candidate_no or "", e.status, e.notes or "", "Xóa")
                for e in exam_service.list_eligibilities(exam_id=values[0])
            ])

    def _exam_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa lịch thi {values[0]}?"):
            exam_service.delete_exam(values[0])
            self.refresh()

    def _eligibility_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values:
            exam_service.delete_eligibility(values[0])
            self.refresh()

    def _grade_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values:
            exam_service.delete_grade(values[0])
            self.refresh()

    def _review_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values:
            exam_service.delete_review(values[0])
            self.refresh()

    def _render_tables(self) -> None:
        self._exam_table.load([(e.exam_id, e.section_id, e.exam_date, e.shift, e.room, e.exam_type, "Xóa") for e in exam_service.list_exams()])
        self._eligibility_table.load([(e.eligibility_id, e.exam_id, e.ma_hs, e.candidate_no or "", e.status, e.notes or "", "Xóa") for e in exam_service.list_eligibilities()])
        self._grade_table.load([(g.grade_id, g.section_id, g.ma_hs, g.component_score or "", g.midterm_score or "", g.final_score or "", g.average10 or "", g.gpa4 or "", g.letter_grade or "", "Xóa") for g in exam_service.list_grades()])
        self._review_table.load([(r.review_id, r.grade_id, r.request_date, r.status, r.adjusted_score or "", r.reason, "Xóa") for r in exam_service.list_reviews()])

    def refresh(self) -> None:
        self._refresh_options()
        summary = exam_service.summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))
        self._render_tables()
        self._set_entry(self._exam_id, exam_service.next_exam_id())
        self._set_entry(self._grade_id, exam_service.next_grade_id())
        self._set_entry(self._review_id, exam_service.next_review_id())
