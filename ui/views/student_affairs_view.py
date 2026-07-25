import customtkinter as ctk
from tkinter import messagebox

from models.student_affairs import (
    ConductScoreInfo,
    DormAssignmentInfo,
    ExtracurricularActivityInfo,
    HealthRecordInfo,
)
from services import student_service, student_affairs_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class StudentAffairsView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._students: dict = {}
        self._metrics: dict = {}
        self._build()

    def _build(self) -> None:
        heading(self, "Công tác sinh viên & Ngoại khóa", size=26).pack(anchor="w", padx=4)
        subheading(self, "Điểm rèn luyện, ký túc xá, ngoại khóa và y tế học đường.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("conduct", "Rèn luyện", "#2563eb", "Ban ghi", "RL"),
                ("dorm", "KTX", "#10b981", "Đang ở", "KTX"),
                ("activities", "Ngoại khóa", "#7c3aed", "Tham gia", "NK"),
                ("health_alerts", "Y tế cần theo dõi", "#ef4444", "Cảnh báo", "YT"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        self._conduct_tab = tabs.add("Rèn luyện")
        self._dorm_tab = tabs.add("KTX")
        self._activity_tab = tabs.add("Ngoại khóa")
        self._health_tab = tabs.add("Y tế")
        self._build_conduct_tab()
        self._build_dorm_tab()
        self._build_activity_tab()
        self._build_health_tab()

        if self._on_navigate:
            ScreenNavBar(self, "affairs", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _build_conduct_tab(self) -> None:
        form, table_area = self._two_col(self._conduct_tab)
        self._conduct_id = self._entry(form, "Mã Điểm RL", student_affairs_service.next_conduct_id())
        self._conduct_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._conduct_term = self._entry(form, "Học kỳ/năm học", "HK1 2026")
        self._awareness = self._entry(form, "Điểm ý thức", "90")
        self._discipline = self._entry(form, "Điểm đạo đức/kỷ luật", "90")
        self._activity_score = self._entry(form, "Điểm hoạt động", "90")
        ctk.CTkButton(form, text="Lưu điểm rèn luyện", command=self._save_conduct, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa điểm rèn luyện đang chọn", command=self._delete_selected_conduct, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._conduct_table = DataTable(table_area, columns=[("id", "Mã", 90), ("student", "HS", 80), ("term", "Kỳ", 100), ("total", "Tổng", 70), ("rating", "Xếp loại", 110)])
        self._conduct_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_dorm_tab(self) -> None:
        form, table_area = self._two_col(self._dorm_tab)
        self._dorm_id = self._entry(form, "Mã KTX", student_affairs_service.next_dorm_id())
        self._dorm_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._building = self._entry(form, "Tòa nhà", "A")
        self._room = self._entry(form, "Phòng", "101")
        self._bed = self._entry(form, "GiĐăng", "01")
        self._start_date = self._entry(form, "Ngày vào ở", "2026-07-22")
        self._electric_water = self._entry(form, "Tiền điện nước", "0")
        self._dorm_status = self._combo(form, "Trạng thái", list(student_affairs_service.DORM_STATUSES))
        ctk.CTkButton(form, text="Lưu KTX", command=self._save_dorm, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa KTX đang chọn", command=self._delete_selected_dorm, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._dorm_table = DataTable(table_area, columns=[("id", "Mã", 90), ("student", "HS", 80), ("building", "Tòa", 60), ("room", "Phòng", 80), ("fee", "Điện nước", 90), ("status", "Trạng thái", 100)])
        self._dorm_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_activity_tab(self) -> None:
        form, table_area = self._two_col(self._activity_tab)
        self._activity_id = self._entry(form, "Mã hoạt động", student_affairs_service.next_activity_id())
        self._activity_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._activity_name = self._entry(form, "Tên hoạt động", "CLB Hoc thuat")
        self._activity_type = self._entry(form, "Loại hoạt động", "CLB")
        self._join_date = self._entry(form, "Ngày tham gia", "2026-07-22")
        self._role = self._entry(form, "Vai trò", "Thanh vien")
        self._hours = self._entry(form, "Số giờ", "4")
        self._activity_status = self._combo(form, "Trạng thái", list(student_affairs_service.ACTIVITY_STATUSES))
        ctk.CTkButton(form, text="Lưu ngoại khóa", command=self._save_activity, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa ngoại khóa đang chọn", command=self._delete_selected_activity, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._activity_table = DataTable(table_area, columns=[("id", "Mã", 90), ("student", "HS", 80), ("name", "Hoạt động", 160), ("type", "Loại", 80), ("hours", "Giờ", 60), ("status", "Trạng thái", 100)])
        self._activity_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_health_tab(self) -> None:
        form, table_area = self._two_col(self._health_tab)
        self._health_id = self._entry(form, "Mã y tế", student_affairs_service.next_health_id())
        self._health_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._checkup_date = self._entry(form, "Ngày khám", "2026-07-22")
        self._height = self._entry(form, "Chiều cao cm", "165")
        self._weight = self._entry(form, "Cân nặng kg", "55")
        self._health_status = self._combo(form, "Trạng thái sức khỏe", list(student_affairs_service.HEALTH_STATUSES))
        self._insurance_no = self._entry(form, "Số BHYT")
        self._insurance_expiry = self._entry(form, "Hạn BHYT", "2027-07-22")
        ctk.CTkButton(form, text="Lưu y tế", command=self._save_health, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa y tế đang chọn", command=self._delete_selected_health, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._health_table = DataTable(table_area, columns=[("id", "Mã", 90), ("student", "HS", 80), ("date", "Ngày", 100), ("height", "Cao", 60), ("weight", "Nặng", 60), ("status", "Sức khỏe", 110), ("insurance", "BHYT", 110)])
        self._health_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _two_col(self, parent):
        parent.grid_columnconfigure(0, weight=0, minsize=330)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        form_card = card(parent, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        table_area = card(parent)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        return form, table_area

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

    def _code(self, combo) -> str:
        return self._students.get(combo.get(), "")

    def _refresh_options(self) -> None:
        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        values = ["Chọn học sinh"] + list(self._students.keys())
        for combo in (self._conduct_student, self._dorm_student, self._activity_student, self._health_student):
            combo.configure(values=values)
            if combo.get() not in values:
                combo.set(values[0])

    def _save_conduct(self):
        try:
            item = ConductScoreInfo(self._conduct_id.get().strip(), self._code(self._conduct_student), self._conduct_term.get().strip(), float(self._awareness.get()), float(self._discipline.get()), float(self._activity_score.get()))
            student_affairs_service.save_conduct_score(item)
            messagebox.showinfo("Thành công", "Đã lưu Điểm rèn luyện.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_dorm(self):
        try:
            item = DormAssignmentInfo(self._dorm_id.get().strip(), self._code(self._dorm_student), self._building.get().strip(), self._room.get().strip(), self._bed.get().strip() or None, self._start_date.get().strip(), None, float(self._electric_water.get() or 0), self._dorm_status.get().strip())
            student_affairs_service.save_dorm_assignment(item)
            messagebox.showinfo("Thành công", "Đã lưu thong tin KTX.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_activity(self):
        try:
            item = ExtracurricularActivityInfo(self._activity_id.get().strip(), self._code(self._activity_student), self._activity_name.get().strip(), self._activity_type.get().strip(), self._join_date.get().strip(), self._role.get().strip() or None, float(self._hours.get() or 0), self._activity_status.get().strip())
            student_affairs_service.save_activity(item)
            messagebox.showinfo("Thành công", "Đã lưu hoat dong ngoại khóa.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_health(self):
        try:
            height = self._height.get().strip()
            weight = self._weight.get().strip()
            item = HealthRecordInfo(self._health_id.get().strip(), self._code(self._health_student), self._checkup_date.get().strip(), float(height) if height else None, float(weight) if weight else None, self._health_status.get().strip(), self._insurance_no.get().strip() or None, self._insurance_expiry.get().strip() or None)
            student_affairs_service.save_health_record(item)
            messagebox.showinfo("Thành công", "Đã lưu hồ sơ y tế.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))


    def _delete_selected_conduct(self):
        values = self._conduct_table.get_selected_values()
        if values:
            self._conduct_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn điểm rèn luyện cần xóa.")

    def _delete_selected_dorm(self):
        values = self._dorm_table.get_selected_values()
        if values:
            self._dorm_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn KTX cần xóa.")

    def _delete_selected_activity(self):
        values = self._activity_table.get_selected_values()
        if values:
            self._activity_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngoại khóa cần xóa.")

    def _delete_selected_health(self):
        values = self._health_table.get_selected_values()
        if values:
            self._health_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hồ sơ y tế cần xóa.")

    def _conduct_action(self, action, values):
        if action == "delete" and values:
            student_affairs_service.delete_conduct_score(values[0])
            self.refresh()

    def _dorm_action(self, action, values):
        if action == "delete" and values:
            student_affairs_service.delete_dorm_assignment(values[0])
            self.refresh()

    def _activity_action(self, action, values):
        if action == "delete" and values:
            student_affairs_service.delete_activity(values[0])
            self.refresh()

    def _health_action(self, action, values):
        if action == "delete" and values:
            student_affairs_service.delete_health_record(values[0])
            self.refresh()

    def _render_tables(self) -> None:
        self._conduct_table.load([(x.conduct_id, x.ma_hs, x.term, f"{x.total_score:g}", x.rating, "Xóa") for x in student_affairs_service.list_conduct_scores()])
        self._dorm_table.load([(x.dorm_id, x.ma_hs, x.building, x.room, f"{x.electric_water_fee:g}", x.status, "Xóa") for x in student_affairs_service.list_dorm_assignments()])
        self._activity_table.load([(x.activity_id, x.ma_hs, x.activity_name, x.activity_type, f"{x.hours:g}", x.status, "Xóa") for x in student_affairs_service.list_activities()])
        self._health_table.load([(x.health_id, x.ma_hs, x.checkup_date, x.height_cm or "", x.weight_kg or "", x.health_status, x.insurance_no or "", "Xóa") for x in student_affairs_service.list_health_records()])

    def refresh(self) -> None:
        self._refresh_options()
        summary = student_affairs_service.summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))
        self._render_tables()
        self._set_entry(self._conduct_id, student_affairs_service.next_conduct_id())
        self._set_entry(self._dorm_id, student_affairs_service.next_dorm_id())
        self._set_entry(self._activity_id, student_affairs_service.next_activity_id())
        self._set_entry(self._health_id, student_affairs_service.next_health_id())
