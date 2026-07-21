import customtkinter as ctk
from tkinter import messagebox

from models.btth06 import BusinessRecordInfo
from services import btth06_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading


class BusinessView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._editing_id: str | None = None
        self._requirements: dict = {}
        self._all_requirement_rows: list = []
        self._all_record_rows: list = []
        self._metrics: dict = {}
        self._requirement_page = None
        self._record_page = None
        self._build()

    def _build(self) -> None:
        heading(self, "Nghiep vu tong hop BTTH06", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Doi chieu 30 yeu cau cot loi va quan ly ho so nghiep vu phat sinh.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(5):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("total", "Tong yeu cau", "#2563eb", "BTTH06", "30"),
                ("implemented", "Da co", "#10b981", "Dang chay trong app", "OK"),
                ("partial", "Mot phan", "#f59e0b", "Can mo rong", "~"),
                ("planned", "Con thieu", "#ef4444", "Backlog", "!"),
                ("records", "Ho so", "#7c3aed", "Dang quan ly", "HS"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_requirement_panel(body)
        self._build_record_panel(body)

        if self._on_navigate:
            ScreenNavBar(self, "business", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _build_requirement_panel(self, parent) -> None:
        panel = card(parent)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=10)
        self._req_search = ctk.CTkEntry(toolbar, placeholder_text="Tim ma/tieu de yeu cau...", height=38)
        self._req_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._req_search.bind("<KeyRelease>", lambda _e: self._on_requirement_filter())
        self._group_filter = ctk.CTkComboBox(toolbar, values=["Tat ca nhom"], width=190, height=38, command=lambda _v: self._on_requirement_filter())
        self._group_filter.pack(side="left", padx=(0, 8))
        self._group_filter.set("Tat ca nhom")
        self._req_status_filter = ctk.CTkComboBox(
            toolbar,
            values=["Tat ca trang thai"] + list(btth06_service.REQUIREMENT_STATUSES),
            width=145,
            height=38,
            command=lambda _v: self._on_requirement_filter(),
        )
        self._req_status_filter.pack(side="left")
        self._req_status_filter.set("Tat ca trang thai")

        self._requirements_table = DataTable(
            panel,
            columns=[
                ("code", "Ma", 70),
                ("group", "Nhom", 170),
                ("title", "Yeu cau", 170),
                ("status", "Trang thai", 95),
                ("module", "Module", 100),
            ],
            on_select=self._on_requirement_select,
        )
        self._requirements_table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._requirement_page = PaginationBar(panel, on_change=self._render_requirement_page, page_size=10)
        self._requirement_page.pack(fill="x", padx=10, pady=(0, 10))

    def _build_record_panel(self, parent) -> None:
        panel = card(parent)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        form = ctk.CTkScrollableFrame(panel, fg_color="transparent", height=260)
        form.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(form, text="Ho so nghiep vu", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")

        self._record_id = self._entry(form, "Ma ho so", disabled=True)
        self._requirement_code = self._combo(form, "Yeu cau BTTH06", ["Chon yeu cau"])
        self._record_title = self._entry(form, "Tieu de ho so")
        self._student_code = self._entry(form, "Ma hoc sinh lien quan (neu co)")
        self._record_status = self._combo(form, "Trang thai", list(btth06_service.RECORD_STATUSES))
        self._event_date = self._entry(form, "Ngay phat sinh (YYYY-MM-DD)")
        self._numeric_value = self._entry(form, "Gia tri so/diem/tin chi (neu co)")
        self._amount = self._entry(form, "So tien (neu co)")
        self._notes = self._entry(form, "Ghi chu")

        self._save_btn = build_form_actions(
            panel,
            self._save_record,
            self._reset_record_form,
            self._delete_record,
            save_text="Luu ho so",
            reset_text="Lam moi",
            delete_text="Xoa ho so da chon",
        )

        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(8, 8))
        self._record_search = ctk.CTkEntry(toolbar, placeholder_text="Tim ho so nghiep vu...", height=36)
        self._record_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._record_search.bind("<KeyRelease>", lambda _e: self._on_record_filter())
        self._record_status_filter = ctk.CTkComboBox(
            toolbar,
            values=["Tat ca"] + list(btth06_service.RECORD_STATUSES),
            width=135,
            height=36,
            command=lambda _v: self._on_record_filter(),
        )
        self._record_status_filter.pack(side="left")
        self._record_status_filter.set("Tat ca")

        self._records_table = DataTable(
            panel,
            columns=[
                ("id", "Ma", 70),
                ("req", "Yeu cau", 80),
                ("title", "Tieu de", 180),
                ("student", "HS", 70),
                ("status", "Trang thai", 90),
                ("actions", "Hanh dong", 90),
            ],
            on_select=self._on_record_select,
            on_action=self._on_record_action,
        )
        self._records_table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._record_page = PaginationBar(panel, on_change=self._render_record_page, page_size=7)
        self._record_page.pack(fill="x", padx=10, pady=(0, 10))

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

    def _set_record_id(self, record_id: str) -> None:
        self._set_entry(self._record_id, record_id)
        self._record_id.configure(state="disabled")

    def _get_record_id(self) -> str:
        self._record_id.configure(state="normal")
        value = self._record_id.get().strip()
        self._record_id.configure(state="disabled")
        return value

    def _parse_float(self, entry) -> float | None:
        value = entry.get().strip()
        return float(value) if value else None

    def _on_requirement_filter(self) -> None:
        self._requirement_page.reset()
        self.refresh()

    def _on_record_filter(self) -> None:
        self._record_page.reset()
        self.refresh()

    def _on_requirement_select(self, values: tuple) -> None:
        if not values:
            return
        self._requirement_code.set(values[0])
        if not self._record_title.get().strip():
            self._record_title.insert(0, values[2])

    def _on_record_select(self, values: tuple) -> None:
        if values:
            self._fill_record_form(values[0])

    def _on_record_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        if action == "edit":
            self._fill_record_form(values[0])
        elif action == "delete":
            self._editing_id = values[0]
            self._delete_record()

    def _fill_record_form(self, record_id: str) -> None:
        record = btth06_service.get_record(record_id)
        if not record:
            return
        self._editing_id = record.record_id
        self._set_record_id(record.record_id)
        self._requirement_code.set(record.requirement_code)
        for entry, value in [
            (self._record_title, record.title),
            (self._student_code, record.student_code or ""),
            (self._event_date, record.event_date or ""),
            (self._numeric_value, "" if record.numeric_value is None else str(record.numeric_value)),
            (self._amount, "" if record.amount is None else str(record.amount)),
            (self._notes, record.notes or ""),
        ]:
            self._set_entry(entry, value)
        self._record_status.set(record.status)
        self._save_btn.configure(text="Cap nhat ho so")

    def _form_to_record(self) -> BusinessRecordInfo:
        return BusinessRecordInfo(
            record_id=self._get_record_id(),
            requirement_code=self._requirement_code.get().strip(),
            title=self._record_title.get().strip(),
            status=self._record_status.get().strip(),
            student_code=self._student_code.get().strip() or None,
            event_date=self._event_date.get().strip() or None,
            numeric_value=self._parse_float(self._numeric_value),
            amount=self._parse_float(self._amount),
            notes=self._notes.get().strip() or None,
        )

    def _save_record(self) -> None:
        try:
            record = self._form_to_record()
            if self._editing_id:
                record.record_id = self._editing_id
                btth06_service.update_record(record)
                messagebox.showinfo("Thanh cong", "Da cap nhat ho so nghiep vu.")
            else:
                btth06_service.create_record(record)
                messagebox.showinfo("Thanh cong", "Da them ho so nghiep vu.")
            self._notify()
            self._reset_record_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Loi", str(e))

    def _delete_record(self) -> None:
        record_id = self._editing_id or self._get_record_id()
        if not record_id:
            messagebox.showwarning("Canh bao", "Vui long chon ho so can xoa.")
            return
        if not messagebox.askyesno("Xac nhan", f"Xoa ho so {record_id}?"):
            return
        try:
            btth06_service.delete_record(record_id)
            messagebox.showinfo("Thanh cong", "Da xoa ho so nghiep vu.")
            self._notify()
            self._reset_record_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Loi", str(e))

    def _reset_record_form(self) -> None:
        self._editing_id = None
        self._set_record_id(btth06_service.generate_next_record_id())
        if self._requirements:
            self._requirement_code.set(next(iter(self._requirements)))
        for entry in (
            self._record_title,
            self._student_code,
            self._event_date,
            self._numeric_value,
            self._amount,
            self._notes,
        ):
            self._set_entry(entry, "")
        self._record_status.set("Moi")
        self._save_btn.configure(text="Luu ho so")

    def _update_metrics(self) -> None:
        summary = btth06_service.requirement_summary()
        self._metrics["total"].set_value(str(summary["total"]))
        self._metrics["implemented"].set_value(str(summary["implemented"]))
        self._metrics["partial"].set_value(str(summary["partial"]))
        self._metrics["planned"].set_value(str(summary["planned"]))
        self._metrics["records"].set_value(str(summary["records"]))

    def _render_requirement_page(self) -> None:
        self._requirements_table.load(self._requirement_page.slice(self._all_requirement_rows))

    def _render_record_page(self) -> None:
        self._records_table.load(self._record_page.slice(self._all_record_rows))

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def refresh(self) -> None:
        self._update_metrics()
        groups = ["Tat ca nhom"] + btth06_service.list_groups()
        self._group_filter.configure(values=groups)
        if self._group_filter.get() not in groups:
            self._group_filter.set("Tat ca nhom")

        group = None if self._group_filter.get() == "Tat ca nhom" else self._group_filter.get()
        req_status = None if self._req_status_filter.get() == "Tat ca trang thai" else self._req_status_filter.get()
        req_search = self._req_search.get().strip() or None
        requirements = btth06_service.list_requirements(group_name=group, status=req_status, search=req_search)
        all_requirements = btth06_service.list_requirements()
        self._requirements = {r.code: r for r in all_requirements}
        requirement_codes = list(self._requirements.keys()) or ["Chon yeu cau"]
        self._requirement_code.configure(values=requirement_codes)
        if self._requirement_code.get() not in requirement_codes:
            self._requirement_code.set(requirement_codes[0])

        self._all_requirement_rows = [
            (r.code, r.group_name, r.title, r.status, r.module_hint or "")
            for r in requirements
        ]
        self._render_requirement_page()

        record_status = None if self._record_status_filter.get() == "Tat ca" else self._record_status_filter.get()
        record_search = self._record_search.get().strip() or None
        records = btth06_service.list_records(status=record_status, search=record_search)
        self._all_record_rows = [
            (
                r.record_id,
                r.requirement_code,
                r.title,
                r.student_code or "",
                r.status,
                "Sua | Xoa",
            )
            for r in records
        ]
        self._render_record_page()
        if not self._get_record_id():
            self._reset_record_form()
