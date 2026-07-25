import customtkinter as ctk
from tkinter import messagebox

from models.graduation import AlumniEmploymentInfo, DiplomaRecordInfo, DocumentRequestInfo, GraduationCheckInfo
from services import graduation_service, student_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class GraduationView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._students: dict = {}
        self._checks: dict = {}
        self._metrics: dict = {}
        self._build()

    def _build(self) -> None:
        heading(self, "Tốt nghiệp & Bao cao", size=26).pack(anchor="w", padx=4)
        subheading(self, "Xét tốt nghiệp, văn bằng, biểu mẫu, thống kê và cựu sinh viên.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi = ctk.CTkFrame(self, fg_color="transparent")
        kpi.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate([
            ("eligible", "Đủ TN", "#10b981", "Đạt điều kiện", "TN"),
            ("diplomas", "Văn bằng", "#2563eb", "Đã quản lý", "VB"),
            ("documents", "Biểu mẫu", "#7c3aed", "Yêu cựu", "BM"),
            ("employed", "Có việc làm", "#f59e0b", "Cựu SV", "VL"),
        ]):
            metric = MetricCard(kpi, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        self._check_tab = tabs.add("Xet TN")
        self._diploma_tab = tabs.add("Văn bằng")
        self._document_tab = tabs.add("Biểu mẫu")
        self._alumni_tab = tabs.add("Cựu SV")
        self._build_check_tab()
        self._build_diploma_tab()
        self._build_document_tab()
        self._build_alumni_tab()

        if self._on_navigate:
            ScreenNavBar(self, "graduation", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _two_col(self, parent):
        parent.grid_columnconfigure(0, weight=0, minsize=330)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        form_card = card(parent, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        table = card(parent)
        table.grid(row=0, column=1, sticky="nsew", pady=10)
        return form, table

    def _build_check_tab(self):
        form, table = self._two_col(self._check_tab)
        self._check_id = self._entry(form, "Mã xét TN", graduation_service.next_check_id())
        self._check_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._check_date = self._entry(form, "Ngày xét", "2026-07-22")
        self._required_credits = self._entry(form, "Tín chỉ yêu cầu", "120")
        self._earned_credits = self._entry(form, "Tín chỉ đạt (-1 để tự tính)", "-1")
        self._informatics = self._combo(form, "Chứng chỉ tin học", ["Có", "Không"])
        self._language = self._combo(form, "Chứng chỉ ngoại ngữ", ["Có", "Không"])
        self._defense = self._combo(form, "GDQP", ["Có", "Không"])
        ctk.CTkButton(form, text="Xét tốt nghiệp", command=self._save_check, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa xét tốt nghiệp đang chọn", command=self._delete_selected_check, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._check_table = DataTable(table, columns=[("id", "Mã", 85), ("student", "HS", 80), ("date", "Ngày", 100), ("credits", "TC", 80), ("certs", "CC", 100), ("status", "Trạng thái", 110)])
        self._check_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_diploma_tab(self):
        form, table = self._two_col(self._diploma_tab)
        self._diploma_id = self._entry(form, "Mã văn bằng", graduation_service.next_diploma_id())
        self._diploma_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._diploma_check = self._combo(form, "Kết quả xét TN", ["Không"])
        self._registry_no = self._entry(form, "Số hiệu sổ gốc", "SG-001")
        self._diploma_no = self._entry(form, "Số hiệu bằng", "VB-001")
        self._issue_date = self._entry(form, "Ngày cóp", "2026-07-22")
        self._diploma_status = self._combo(form, "Trạng thái", list(graduation_service.DIPLOMA_STATUSES))
        ctk.CTkButton(form, text="Lưu văn bằng", command=self._save_diploma, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa văn bằng đang chọn", command=self._delete_selected_diploma, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._diploma_table = DataTable(table, columns=[("id", "Mã", 85), ("student", "HS", 80), ("registry", "Số gốc", 100), ("diploma", "Số bằng", 100), ("date", "Ngày", 100), ("status", "Trạng thái", 100)])
        self._diploma_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_document_tab(self):
        form, table = self._two_col(self._document_tab)
        self._document_id = self._entry(form, "Mã biểu mẫu", graduation_service.next_document_id())
        self._document_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._document_type = self._combo(form, "Loại biểu mẫu", list(graduation_service.DOCUMENT_TYPES))
        self._document_date = self._entry(form, "Ngày yêu cầu", "2026-07-22")
        self._document_status = self._combo(form, "Trạng thái", list(graduation_service.DOCUMENT_STATUSES))
        ctk.CTkButton(form, text="Lưu yêu cầu biểu mẫu", command=self._save_document, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xem thống kê EMIS", command=self._show_emis, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa biểu mẫu đang chọn", command=self._delete_selected_document, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._document_table = DataTable(table, columns=[("id", "Mã", 85), ("student", "HS", 80), ("type", "Loại", 140), ("date", "Ngày", 100), ("status", "Trạng thái", 100), ("path", "Đường dẫn", 170)])
        self._document_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_alumni_tab(self):
        form, table = self._two_col(self._alumni_tab)
        self._alumni_id = self._entry(form, "Mã khảo sốt", graduation_service.next_alumni_id())
        self._alumni_student = self._combo(form, "Học sinh/Cựu SV", ["Chọn học sinh"])
        self._survey_date = self._entry(form, "Ngày khao sat", "2026-07-22")
        self._employment_status = self._combo(form, "Trạng thái việc làm", list(graduation_service.EMPLOYMENT_STATUSES))
        self._company = self._entry(form, "Công ty")
        self._position = self._entry(form, "Vị trí")
        self._salary = self._entry(form, "Lương")
        ctk.CTkButton(form, text="Lưu việc làm cựu SV", command=self._save_alumni, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa việc làm đang chọn", command=self._delete_selected_alumni, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))
        self._alumni_table = DataTable(table, columns=[("id", "Mã", 90), ("student", "HS", 80), ("date", "Ngày", 100), ("status", "Trạng thái", 130), ("company", "Công ty", 130), ("position", "Vị trí", 110)])
        self._alumni_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _entry(self, parent, label, value=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        e = ctk.CTkEntry(parent, placeholder_text=label, height=36)
        e.insert(0, value)
        e.pack(fill="x", padx=12, pady=(2, 0))
        return e

    def _combo(self, parent, label, values):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        c = ctk.CTkComboBox(parent, values=values, height=36)
        c.set(values[0])
        c.pack(fill="x", padx=12, pady=(2, 0))
        return c

    def _set_entry(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def _code(self, combo):
        return self._students.get(combo.get(), "")

    def _check_code(self):
        return self._checks.get(self._diploma_check.get())

    def _refresh_options(self):
        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        values = ["Chọn học sinh"] + list(self._students.keys())
        for combo in (self._check_student, self._diploma_student, self._document_student, self._alumni_student):
            combo.configure(values=values)
            if combo.get() not in values:
                combo.set(values[0])
        checks = graduation_service.list_checks()
        self._checks = {f"{c.check_id} - {c.ma_hs} - {c.status}": c.check_id for c in checks}
        check_values = ["Không"] + list(self._checks.keys())
        self._diploma_check.configure(values=check_values)
        if self._diploma_check.get() not in check_values:
            self._diploma_check.set(check_values[0])

    def _save_check(self):
        try:
            item = GraduationCheckInfo(self._check_id.get().strip(), self._code(self._check_student), self._check_date.get().strip(), int(self._required_credits.get()), int(self._earned_credits.get()), self._informatics.get() == "Có", self._language.get() == "Có", self._defense.get() == "Có")
            graduation_service.check_graduation(item)
            messagebox.showinfo("Thành công", f"Kết quả: {item.status}")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_diploma(self):
        try:
            item = DiplomaRecordInfo(self._diploma_id.get().strip(), self._code(self._diploma_student), self._registry_no.get().strip(), self._diploma_no.get().strip(), self._issue_date.get().strip(), self._diploma_status.get().strip(), self._check_code())
            graduation_service.save_diploma(item)
            messagebox.showinfo("Thành công", "Đã lưu văn bằng.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_document(self):
        try:
            item = DocumentRequestInfo(self._document_id.get().strip(), self._code(self._document_student), self._document_type.get().strip(), self._document_date.get().strip(), self._document_status.get().strip())
            graduation_service.save_document_request(item)
            messagebox.showinfo("Thành công", "Đã lưu yêu cầu biểu mẫu.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_alumni(self):
        try:
            salary_text = self._salary.get().strip()
            item = AlumniEmploymentInfo(self._alumni_id.get().strip(), self._code(self._alumni_student), self._survey_date.get().strip(), self._employment_status.get().strip(), self._company.get().strip() or None, self._position.get().strip() or None, float(salary_text) if salary_text else None)
            graduation_service.save_alumni(item)
            messagebox.showinfo("Thành công", "Đã lưu việc làm cựu sinh viên.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _show_emis(self):
        data = graduation_service.emis_report()
        messagebox.showinfo("Thứng kỳ EMIS", "\n".join(f"{k}: {v}" for k, v in data.items()))


    def _delete_selected_check(self):
        values = self._check_table.get_selected_values()
        if values:
            self._check_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn kết quả tốt nghiệp cần xóa.")

    def _delete_selected_diploma(self):
        values = self._diploma_table.get_selected_values()
        if values:
            self._diploma_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn văn bằng cần xóa.")

    def _delete_selected_document(self):
        values = self._document_table.get_selected_values()
        if values:
            self._document_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biểu mẫu cần xóa.")

    def _delete_selected_alumni(self):
        values = self._alumni_table.get_selected_values()
        if values:
            self._alumni_action("delete", values)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn việc làm cựu sinh viên cần xóa.")

    def _check_action(self, action, values):
        if action == "delete" and values:
            graduation_service.delete_check(values[0]); self.refresh()

    def _diploma_action(self, action, values):
        if action == "delete" and values:
            graduation_service.delete_diploma(values[0]); self.refresh()

    def _document_action(self, action, values):
        if action == "delete" and values:
            graduation_service.delete_document(values[0]); self.refresh()

    def _alumni_action(self, action, values):
        if action == "delete" and values:
            graduation_service.delete_alumni(values[0]); self.refresh()

    def _render_tables(self):
        self._check_table.load([(x.check_id, x.ma_hs, x.check_date, f"{x.earned_credits}/{x.required_credits}", f"Tin:{x.informatics_cert} NN:{x.language_cert} QP:{x.defense_cert}", x.status, "Xóa") for x in graduation_service.list_checks()])
        self._diploma_table.load([(x.diploma_id, x.ma_hs, x.registry_no, x.diploma_no, x.issue_date, x.status, "Xóa") for x in graduation_service.list_diplomas()])
        self._document_table.load([(x.request_id, x.ma_hs, x.document_type, x.request_date, x.status, x.output_path or "", "Xóa") for x in graduation_service.list_documents()])
        self._alumni_table.load([(x.alumni_id, x.ma_hs, x.survey_date, x.employment_status, x.company or "", x.position or "", "Xóa") for x in graduation_service.list_alumni()])

    def refresh(self):
        self._refresh_options()
        summary = graduation_service.summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))
        self._render_tables()
        self._set_entry(self._check_id, graduation_service.next_check_id())
        self._set_entry(self._diploma_id, graduation_service.next_diploma_id())
        self._set_entry(self._document_id, graduation_service.next_document_id())
        self._set_entry(self._alumni_id, graduation_service.next_alumni_id())
