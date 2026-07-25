import customtkinter as ctk
from tkinter import messagebox

from models.admission import AdmissionApplicationInfo
from services import admission_service, school_class_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading


class AdmissionsView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._editing_id: str | None = None
        self._class_map: dict = {}
        self._all_rows: list = []
        self._metrics: dict = {}
        self._pagination = None
        self._pending_new = False
        self._build()

    def _build(self) -> None:
        heading(self, "Quản lý Tuyển sinh & Nhập học", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Tiếp nhận hồ sơ, xét tuyển tự động, cấp mã học sinh và phân lớp.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(5):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("total", "Tổng hồ sơ", "#2563eb", "Tuyển sinh", "HS"),
                ("new", "Mới", "#7c3aed", "Cho xét tuyển", "M"),
                ("passed", "Đạt", "#10b981", "Có thể nhập học", "D"),
                ("failed", "Không Đạt", "#ef4444", "Không Đủ điều kiện", "!"),
                ("enrolled", "Đã nhập học", "#f59e0b", "Đã cấp mã HS", "IN"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=380)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_list(body)

        if self._on_navigate:
            ScreenNavBar(self, "admissions", self._on_navigate).pack(fill="x", pady=(4, 0))

        self._reset_form()

    def _build_form(self, parent) -> None:
        form_card = card(parent, width=380)
        form_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        form_scroll = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(form_scroll, text="Hồ sơ xét tuyển", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=4, pady=(8, 8)
        )
        self._application_id = self._entry(form_scroll, "Mã hồ sơ", disabled=True)
        self._full_name = self._entry(form_scroll, "Họ tên thí sinh")
        self._gender = self._combo(form_scroll, "Giới tính", ["", "Nam", "Nu"])
        self._dob = self._entry(form_scroll, "Ngày sinh (YYYY-MM-DD)")
        self._address = self._entry(form_scroll, "Địa chỉ")
        self._phone = self._entry(form_scroll, "Số điện thoại thí sinh")
        self._parent_name = self._entry(form_scroll, "Họ tên phụ huynh")
        self._parent_phone = self._entry(form_scroll, "Số điện thoại phụ huynh")
        self._admission_score = self._entry(form_scroll, "Điểm xét tuyển (0-10)")
        self._desired_class = self._combo(form_scroll, "Lớp dự kiến", ["Chọn lớp"])
        self._desired_major = self._entry(form_scroll, "Ngành/hướng học nếu có")
        self._status = self._combo(form_scroll, "Trạng thái", list(admission_service.APPLICATION_STATUSES))
        self._notes = self._entry(form_scroll, "Ghi chú")

        self._save_btn = build_form_actions(
            form_card,
            self._save,
            self._reset_form,
            self._delete,
            save_text="Lưu hồ sơ",
            reset_text="Làm mới form",
            delete_text="Xóa hồ sơ đã chọn",
        )

        action_bar = ctk.CTkFrame(form_card, fg_color="transparent")
        action_bar.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(
            action_bar,
            text="Xét tuyển tự động",
            height=36,
            corner_radius=10,
            command=self._screen_selected,
            **primary_button_kwargs(),
        ).pack(fill="x", pady=(0, 6))
        ctk.CTkButton(
            action_bar,
            text="Nhập học & cấp mã HS",
            height=36,
            corner_radius=10,
            command=self._enroll_selected,
            **primary_button_kwargs(),
        ).pack(fill="x")

    def _build_list(self, parent) -> None:
        list_card = card(parent)
        list_card.grid(row=0, column=1, sticky="nsew")

        toolbar = ctk.CTkFrame(list_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=10)
        self._search = ctk.CTkEntry(toolbar, placeholder_text="Tim theo mã hồ sơ, ho tên hoac số dien thoai...", height=38)
        self._search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._search.bind("<KeyRelease>", lambda _e: self._on_filter_change())
        self._status_filter = ctk.CTkComboBox(
            toolbar,
            values=["Tat ca"] + list(admission_service.APPLICATION_STATUSES),
            width=145,
            height=38,
            command=lambda _v: self._on_filter_change(),
        )
        self._status_filter.pack(side="left", padx=(0, 8))
        self._status_filter.set("Tat ca")
        ctk.CTkButton(
            toolbar,
            text="+ Hồ sơ",
            height=38,
            corner_radius=10,
            command=self._on_new_clicked,
            **primary_button_kwargs(),
        ).pack(side="left")

        self._table = DataTable(
            list_card,
            columns=[
                ("id", "Mã", 70),
                ("name", "Thi sinh", 150),
                ("score", "Điểm", 70),
                ("class", "Lớp", 100),
                ("major", "Nganh", 110),
                ("status", "Trạng thái", 105),
                ("student", "Mã HS", 80),
            ],
            on_select=self._on_row_select,
        )
        self._table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._empty_label = ctk.CTkLabel(
            list_card,
            text="Không tìm thấy hồ sơ tuyển sinh phù hợp.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )
        self._pagination = PaginationBar(list_card, on_change=self._render_page, page_size=8)
        self._pagination.pack(fill="x", padx=10, pady=(0, 10))

    def _entry(self, parent, label: str, disabled: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=38)
        if disabled:
            entry.configure(state="disabled")
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=38)
        if values:
            combo.set(values[0])
        combo.pack(fill="x", pady=(2, 0))
        return combo

    def _set_entry(self, entry, value: str) -> None:
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, value)

    def _set_application_id(self, application_id: str) -> None:
        self._set_entry(self._application_id, application_id)
        self._application_id.configure(state="disabled")

    def _get_application_id(self) -> str:
        self._application_id.configure(state="normal")
        value = self._application_id.get().strip()
        self._application_id.configure(state="disabled")
        return value

    def _gender_to_int(self, text: str) -> int | None:
        return 1 if text == "Nam" else 0 if text == "Nu" else None

    def _parse_score(self) -> float | None:
        value = self._admission_score.get().strip()
        return float(value) if value else None

    def _load_class_options(self) -> None:
        classes = school_class_service.list_classes()
        self._class_map = {f"{c.ten_lop} ({c.ma_lop})": c.ma_lop for c in classes}
        values = ["Chọn lớp"] + list(self._class_map.keys())
        self._desired_class.configure(values=values)
        if self._desired_class.get() not in values:
            self._desired_class.set("Chọn lớp")

    def _get_selected_class(self) -> str | None:
        return self._class_map.get(self._desired_class.get())

    def _form_to_model(self) -> AdmissionApplicationInfo:
        return AdmissionApplicationInfo(
            application_id=self._get_application_id(),
            full_name=self._full_name.get().strip(),
            gender=self._gender_to_int(self._gender.get()),
            dob=self._dob.get().strip() or None,
            address=self._address.get().strip() or None,
            phone=self._phone.get().strip() or None,
            parent_name=self._parent_name.get().strip() or None,
            parent_phone=self._parent_phone.get().strip() or None,
            admission_score=self._parse_score(),
            desired_class=self._get_selected_class(),
            desired_major=self._desired_major.get().strip() or None,
            status=self._status.get().strip() or "Mới",
            notes=self._notes.get().strip() or None,
        )

    def _fill_form(self, app: AdmissionApplicationInfo) -> None:
        self._editing_id = app.application_id
        self._pending_new = False
        self._set_application_id(app.application_id)
        for entry, value in [
            (self._full_name, app.full_name),
            (self._dob, app.dob or ""),
            (self._address, app.address or ""),
            (self._phone, app.phone or ""),
            (self._parent_name, app.parent_name or ""),
            (self._parent_phone, app.parent_phone or ""),
            (self._admission_score, "" if app.admission_score is None else str(app.admission_score)),
            (self._desired_major, app.desired_major or ""),
            (self._notes, app.notes or ""),
        ]:
            self._set_entry(entry, value)
        self._gender.set(app.gender_text)
        self._status.set(app.status)
        self._desired_class.set("Chọn lớp")
        for label, code in self._class_map.items():
            if code == app.desired_class:
                self._desired_class.set(label)
                break
        self._save_btn.configure(text="Cập nhật hồ sơ")

    def _clear_form_fields(self) -> None:
        for entry in (
            self._full_name,
            self._dob,
            self._address,
            self._phone,
            self._parent_name,
            self._parent_phone,
            self._admission_score,
            self._desired_major,
            self._notes,
        ):
            self._set_entry(entry, "")
        self._gender.set("")
        self._status.set("Mới")
        self._desired_class.set("Chọn lớp")

    def _reset_form(self) -> None:
        self._editing_id = None
        self._pending_new = False
        self._set_application_id(admission_service.generate_next_id())
        self._clear_form_fields()
        self._save_btn.configure(text="Lưu hồ sơ")

    def _on_new_clicked(self) -> None:
        self._editing_id = None
        self._pending_new = True
        self._set_application_id(admission_service.generate_next_id())
        self._clear_form_fields()
        self._save_btn.configure(text="Lưu hồ sơ")

    def _on_filter_change(self) -> None:
        self._pagination.reset()
        self.refresh()

    def _on_row_select(self, values: tuple) -> None:
        if not values:
            return
        app = admission_service.get_application(values[0])
        if app:
            self._fill_form(app)

    def _on_table_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        if action == "edit":
            app = admission_service.get_application(values[0])
            if app:
                self._fill_form(app)
        elif action == "delete":
            self._editing_id = values[0]
            self._delete()

    def _save(self) -> None:
        try:
            app = self._form_to_model()
            if self._editing_id:
                app.application_id = self._editing_id
                admission_service.update_application(app)
                messagebox.showinfo("Thành công", "Đã cập nhật hồ sơ tuyển sinh.")
            else:
                admission_service.create_application(app)
                messagebox.showinfo("Thành công", "Đã tiếp nhận hồ sơ tuyển sinh.")
            self._notify()
            self._reset_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete(self) -> None:
        application_id = self._editing_id or self._get_application_id()
        if not application_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hồ sơ cần xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Xóa hồ sơ {application_id}?"):
            return
        try:
            admission_service.delete_application(application_id)
            messagebox.showinfo("Thành công", "Đã xóa hồ sơ tuyển sinh.")
            self._notify()
            self._reset_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _screen_selected(self) -> None:
        application_id = self._editing_id or self._get_application_id()
        if not application_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hồ sơ cần xét tuyển.")
            return
        try:
            app = admission_service.auto_screen_application(application_id)
            messagebox.showinfo("Kết quả xét tuyển", f"Hồ sơ {app.application_id}: {app.status}.")
            self._fill_form(app)
            self._notify()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _enroll_selected(self) -> None:
        application_id = self._editing_id or self._get_application_id()
        if not application_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hồ sơ cần nhập học.")
            return
        try:
            student = admission_service.enroll_application(application_id, self._get_selected_class())
            messagebox.showinfo("Nhập học thành công", f"Đã cấp mã học sinh {student.ma_hs}.")
            self._notify()
            app = admission_service.get_application(application_id)
            if app:
                self._fill_form(app)
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _update_metrics(self) -> None:
        summary = admission_service.admission_summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))

    def _render_page(self) -> None:
        page_rows = self._pagination.slice(self._all_rows)
        self._table.load(page_rows)
        if page_rows:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(fill="x", padx=16, pady=(2, 10))

    def refresh(self) -> None:
        self._load_class_options()
        self._update_metrics()
        status = None if self._status_filter.get() == "Tat ca" else self._status_filter.get()
        search = self._search.get().strip() or None
        apps = admission_service.list_applications(status=status, search=search)
        class_names = {c.ma_lop: c.ten_lop for c in school_class_service.list_classes()}
        self._all_rows = [
            (
                app.application_id,
                app.full_name,
                "" if app.admission_score is None else f"{app.admission_score:g}",
                class_names.get(app.desired_class, app.desired_class or ""),
                app.desired_major or "",
                app.status,
                app.student_code or "",
                "Sửa | Xóa",
            )
            for app in apps
        ]
        self._render_page()
