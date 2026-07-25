import customtkinter as ctk
from tkinter import messagebox

from models.student_decision import StudentDecisionInfo
from services import student_service, school_class_service, student_decision_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading


class StudentProfilesView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._student_map: dict = {}
        self._class_map: dict = {}
        self._editing_decision_id: str | None = None
        self._all_decision_rows: list = []
        self._metrics: dict = {}
        self._decision_page = None
        self._build()

    def _build(self) -> None:
        heading(self, "Hồ sơ & Thông tin cá nhân", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Cập nhật lý lịch, trạng thái học tập, diện chính sách và quyết định học sinh.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("students", "Tổng HS", "#2563eb", "Đang quản lý", "HS"),
                ("active", "Đang học", "#10b981", "Trạng thái", "OK"),
                ("policy", "Diện CS", "#f59e0b", "Cần theo dõi", "CS"),
                ("decisions", "Quyết định", "#7c3aed", "Khen thưởng/Kỷ luật", "QD"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=390)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_profile_panel(body)
        self._build_decision_panel(body)

        if self._on_navigate:
            ScreenNavBar(self, "profiles", self._on_navigate).pack(fill="x", pady=(4, 0))

    def _build_profile_panel(self, parent) -> None:
        panel = card(parent, width=390)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        form.pack(fill="both", expand=True)

        ctk.CTkLabel(form, text="Ly lịch học sinh", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=4, pady=(8, 8)
        )
        self._student_combo = self._combo(form, "Chọn học sinh", ["Chọn học sinh"])
        self._student_combo.configure(command=lambda _v: self._load_selected_student())
        self._ma_hs = self._entry(form, "Mã học sinh", disabled=True)
        self._ho_ten = self._entry(form, "Họ tên")
        self._gender = self._combo(form, "Giái tênh", ["", "Nam", "Nu"])
        self._dob = self._entry(form, "Ngày sinh (YYYY-MM-DD)")
        self._address = self._entry(form, "Địa chỉ lien lac")
        self._household = self._entry(form, "Hộ khẩu")
        self._parent_name = self._entry(form, "Họ tên phụ huynh")
        self._parent_phone = self._entry(form, "Số điện thoại phụ huynh")
        self._class_combo = self._combo(form, "Lớp", ["Chọn lớp"])
        self._status = self._combo(form, "Trạng thái học tập", list(student_service.LEARNING_STATUSES))
        self._policy = self._combo(form, "Diện chính sách", list(student_service.POLICY_TYPES))

        ctk.CTkButton(
            panel,
            text="Lưu lý lịch",
            height=38,
            corner_radius=10,
            command=self._save_profile,
            **primary_button_kwargs(),
        ).pack(fill="x", padx=12, pady=12)

    def _build_decision_panel(self, parent) -> None:
        panel = card(parent)
        panel.grid(row=0, column=1, sticky="nsew")

        form = ctk.CTkScrollableFrame(panel, fg_color="transparent", height=235)
        form.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(form, text="Khen thưởng / Kỷ luật", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        self._decision_id = self._entry(form, "Mã quyết định", disabled=True)
        self._decision_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._decision_type = self._combo(form, "Loại quyết định", list(student_decision_service.DECISION_TYPES))
        self._decision_date = self._entry(form, "Ngày quyết định (YYYY-MM-DD)")
        self._decision_title = self._entry(form, "Noi dung quyết định")
        self._decision_issuer = self._entry(form, "Don vi ban hanh")
        self._decision_description = self._entry(form, "Mô tả/Ghi chỉ")

        self._decision_save_btn = build_form_actions(
            panel,
            self._save_decision,
            self._reset_decision_form,
            self._delete_decision,
            save_text="Lưu quyết định",
            reset_text="Làm mới",
            delete_text="Xóa quyết định đã chọn",
        )

        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(8, 8))
        self._decision_search = ctk.CTkEntry(toolbar, placeholder_text="Tim quyết định...", height=36)
        self._decision_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._decision_search.bind("<KeyRelease>", lambda _e: self._on_decision_filter())
        self._decision_type_filter = ctk.CTkComboBox(
            toolbar,
            values=["Tat ca"] + list(student_decision_service.DECISION_TYPES),
            width=135,
            height=36,
            command=lambda _v: self._on_decision_filter(),
        )
        self._decision_type_filter.pack(side="left")
        self._decision_type_filter.set("Tat ca")

        self._decision_table = DataTable(
            panel,
            columns=[
                ("id", "Mã", 70),
                ("student", "HS", 70),
                ("type", "Loại", 100),
                ("date", "Ngày", 95),
                ("title", "Noi dung", 190),
                ("issuer", "Don vi", 100),
            ],
            on_select=self._on_decision_select,
        )
        self._decision_table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._decision_empty = ctk.CTkLabel(
            panel,
            text="Chỉa có quyết định phù hợp.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )
        self._decision_page = PaginationBar(panel, on_change=self._render_decision_page, page_size=7)
        self._decision_page.pack(fill="x", padx=10, pady=(0, 10))

    def _entry(self, parent, label: str, disabled: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=36)
        if disabled:
            entry.configure(state="disabled")
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=36)
        if values:
            combo.set(values[0])
        combo.pack(fill="x", pady=(2, 0))
        return combo

    def _set_entry(self, entry, value: str) -> None:
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, value)

    def _get_disabled_entry(self, entry) -> str:
        entry.configure(state="normal")
        value = entry.get().strip()
        entry.configure(state="disabled")
        return value

    def _set_disabled_entry(self, entry, value: str) -> None:
        self._set_entry(entry, value)
        entry.configure(state="disabled")

    def _gender_to_int(self, text: str) -> int | None:
        return 1 if text == "Nam" else 0 if text == "Nu" else None

    def _load_options(self) -> None:
        students = student_service.list_students()
        self._student_map = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        student_values = ["Chọn học sinh"] + list(self._student_map.keys())
        for combo in (self._student_combo, self._decision_student):
            combo.configure(values=student_values)
            if combo.get() not in student_values:
                combo.set("Chọn học sinh")

        classes = school_class_service.list_classes()
        self._class_map = {f"{c.ten_lop} ({c.ma_lop})": c.ma_lop for c in classes}
        class_values = ["Chọn lớp"] + list(self._class_map.keys())
        self._class_combo.configure(values=class_values)
        if self._class_combo.get() not in class_values:
            self._class_combo.set("Chọn lớp")

    def _student_label_for_code(self, ma_hs: str | None) -> str:
        for label, code in self._student_map.items():
            if code == ma_hs:
                return label
        return "Chọn học sinh"

    def _class_label_for_code(self, ma_lop: str | None) -> str:
        for label, code in self._class_map.items():
            if code == ma_lop:
                return label
        return "Chọn lớp"

    def _selected_student_code(self) -> str | None:
        return self._student_map.get(self._student_combo.get())

    def _selected_decision_student_code(self) -> str | None:
        return self._student_map.get(self._decision_student.get())

    def _selected_class_code(self) -> str | None:
        return self._class_map.get(self._class_combo.get())

    def _load_selected_student(self) -> None:
        ma_hs = self._selected_student_code()
        if not ma_hs:
            return
        student = student_service.get_student(ma_hs)
        if not student:
            return
        self._set_disabled_entry(self._ma_hs, student.ma_hs)
        for entry, value in [
            (self._ho_ten, student.ho_ten),
            (self._dob, student.ngay_sinh or ""),
            (self._address, student.dia_chi or ""),
            (self._household, student.ho_khau or ""),
            (self._parent_name, student.parent_name or ""),
            (self._parent_phone, student.parent_phone or ""),
        ]:
            self._set_entry(entry, value)
        self._gender.set(student.gioi_tinh_text)
        self._class_combo.set(self._class_label_for_code(student.ma_lop))
        self._status.set(student.learning_status or "Đang học")
        self._policy.set(student.policy_type or "Không")
        self._decision_student.set(self._student_label_for_code(student.ma_hs))
        self._on_decision_filter()

    def _save_profile(self) -> None:
        ma_hs = self._get_disabled_entry(self._ma_hs)
        if not ma_hs:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn học sinh.")
            return
        old = student_service.get_student(ma_hs)
        if not old:
            messagebox.showerror("Lỗi", "Không tìm thấy học sinh đã chọn.")
            return
        old.ho_ten = self._ho_ten.get().strip()
        old.gioi_tinh = self._gender_to_int(self._gender.get())
        old.ngay_sinh = self._dob.get().strip() or None
        old.dia_chi = self._address.get().strip() or None
        old.ma_lop = self._selected_class_code()
        old.ho_khau = self._household.get().strip() or None
        old.parent_name = self._parent_name.get().strip() or None
        old.parent_phone = self._parent_phone.get().strip() or None
        old.learning_status = self._status.get().strip()
        old.policy_type = self._policy.get().strip()
        try:
            student_service.update_student_profile(old)
            messagebox.showinfo("Thành công", "Đã cập nhật ly lịch học sinh.")
            self._notify()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _decision_form_to_model(self) -> StudentDecisionInfo:
        return StudentDecisionInfo(
            decision_id=self._get_disabled_entry(self._decision_id),
            ma_hs=self._selected_decision_student_code() or "",
            decision_type=self._decision_type.get().strip(),
            decision_date=self._decision_date.get().strip(),
            title=self._decision_title.get().strip(),
            description=self._decision_description.get().strip() or None,
            issuer=self._decision_issuer.get().strip() or None,
        )

    def _fill_decision_form(self, decision_id: str) -> None:
        decision = student_decision_service.get_decision(decision_id)
        if not decision:
            return
        self._editing_decision_id = decision.decision_id
        self._set_disabled_entry(self._decision_id, decision.decision_id)
        self._decision_student.set(self._student_label_for_code(decision.ma_hs))
        self._decision_type.set(decision.decision_type)
        for entry, value in [
            (self._decision_date, decision.decision_date),
            (self._decision_title, decision.title),
            (self._decision_issuer, decision.issuer or ""),
            (self._decision_description, decision.description or ""),
        ]:
            self._set_entry(entry, value)
        self._decision_save_btn.configure(text="Cập nhật quyết định")

    def _reset_decision_form(self) -> None:
        self._editing_decision_id = None
        self._set_disabled_entry(self._decision_id, student_decision_service.generate_next_id())
        selected_student = self._student_combo.get()
        self._decision_student.set(selected_student if selected_student in self._decision_student.cget("values") else "Chọn học sinh")
        self._decision_type.set("Khen thưởng")
        for entry in (
            self._decision_date,
            self._decision_title,
            self._decision_issuer,
            self._decision_description,
        ):
            self._set_entry(entry, "")
        self._decision_save_btn.configure(text="Lưu quyết định")

    def _save_decision(self) -> None:
        try:
            decision = self._decision_form_to_model()
            if self._editing_decision_id:
                decision.decision_id = self._editing_decision_id
                student_decision_service.update_decision(decision)
                messagebox.showinfo("Thành công", "Đã cập nhật quyết định.")
            else:
                student_decision_service.create_decision(decision)
                messagebox.showinfo("Thành công", "Đã thêm quyết định.")
            self._notify()
            self._reset_decision_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete_decision(self) -> None:
        decision_id = self._editing_decision_id or self._get_disabled_entry(self._decision_id)
        if not decision_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn quyết định cần xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Xóa quyết định {decision_id}?"):
            return
        try:
            student_decision_service.delete_decision(decision_id)
            messagebox.showinfo("Thành công", "Đã xóa quyết định.")
            self._notify()
            self._reset_decision_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _on_decision_select(self, values: tuple) -> None:
        if values:
            self._fill_decision_form(values[0])

    def _on_decision_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        if action == "edit":
            self._fill_decision_form(values[0])
        elif action == "delete":
            self._editing_decision_id = values[0]
            self._delete_decision()

    def _on_decision_filter(self) -> None:
        self._decision_page.reset()
        self.refresh()

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _update_metrics(self) -> None:
        students = student_service.list_students()
        decisions = student_decision_service.decision_summary()
        self._metrics["students"].set_value(str(len(students)))
        self._metrics["active"].set_value(str(len([s for s in students if s.learning_status == "Đang học"])))
        self._metrics["policy"].set_value(str(len([s for s in students if s.policy_type and s.policy_type != "Không"])))
        self._metrics["decisions"].set_value(str(decisions["total"]))

    def _render_decision_page(self) -> None:
        page_rows = self._decision_page.slice(self._all_decision_rows)
        self._decision_table.load(page_rows)
        if page_rows:
            self._decision_empty.pack_forget()
        else:
            self._decision_empty.pack(fill="x", padx=16, pady=(2, 10))

    def refresh(self) -> None:
        self._load_options()
        self._update_metrics()
        decision_type = None if self._decision_type_filter.get() == "Tat ca" else self._decision_type_filter.get()
        ma_hs = self._selected_student_code()
        search = self._decision_search.get().strip() or None
        decisions = student_decision_service.list_decisions(
            ma_hs=ma_hs,
            decision_type=decision_type,
            search=search,
        )
        self._all_decision_rows = [
            (
                d.decision_id,
                d.ma_hs,
                d.decision_type,
                d.decision_date,
                d.title,
                d.issuer or "",
                "Sốa | Xóa",
            )
            for d in decisions
        ]
        self._render_decision_page()
        if not self._get_disabled_entry(self._decision_id):
            self._reset_decision_form()
