import customtkinter as ctk
from tkinter import messagebox

from models.finance import PaymentRecordInfo, TuitionInvoiceInfo
from services import finance_service, student_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class FinanceView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._students: dict = {}
        self._invoices: dict = {}
        self._metrics: dict = {}
        self._build()

    def _build(self) -> None:
        heading(self, "Tài chính & Học phí", size=26).pack(anchor="w", padx=4)
        subheading(
            self,
            "Lập hóa đơn, ghi nhận thanh toán, theo dõi công nợ và xét học bổng.",
        ).pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate(
            [
                ("invoices", "Hóa đơn", "#2563eb", "Đã lập", "HD"),
                ("revenue", "Đã thu", "#10b981", "Tổng tiền", "$"),
                ("debt", "Công nợ", "#ef4444", "Chưa thu", "!"),
                ("scholarships", "Học bổng", "#7c3aed", "Đề xuất", "HB"),
            ]
        ):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        self._invoice_tab = tabs.add("Học phí")
        self._payment_tab = tabs.add("Thanh toán")
        self._scholarship_tab = tabs.add("Học bổng")
        self._build_invoice_tab()
        self._build_payment_tab()
        self._build_scholarship_tab()

        if self._on_navigate:
            ScreenNavBar(self, "finance", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _build_invoice_tab(self) -> None:
        self._invoice_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._invoice_tab.grid_columnconfigure(1, weight=1)
        self._invoice_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._invoice_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._invoice_id = self._entry(form, "Mã hóa đơn", finance_service.next_invoice_id())
        self._invoice_student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._term = self._entry(form, "Học kỳ/Năm học", "HK1 2026")
        self._invoice_type = self._combo(form, "Loại tính phí", list(finance_service.INVOICE_TYPES))
        self._credit_count = self._entry(form, "Số tín chỉ (bỏ trống để tự tính)")
        self._unit_price = self._entry(form, "Đơn giá tín chỉ", "350000")
        self._fixed_amount = self._entry(form, "Mức thu cố định", "2000000")
        self._due_date = self._entry(form, "Hạn thanh toán", "2026-08-15")
        ctk.CTkButton(form, text="Lớp hóa đơn", command=self._save_invoice, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa hóa đơn đang chọn", command=self._delete_selected_invoice, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._invoice_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._invoice_table = DataTable(
            table_area,
            columns=[("id", "Mã", 85), ("student", "HS", 80), ("term", "Kỳ", 100), ("type", "Loại", 110), ("total", "Tổng", 90), ("paid", "Đã thu", 90), ("status", "Trạng thái", 130)],
        )
        self._invoice_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_payment_tab(self) -> None:
        self._payment_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._payment_tab.grid_columnconfigure(1, weight=1)
        self._payment_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._payment_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._payment_id = self._entry(form, "Mã thanh toán", finance_service.next_payment_id())
        self._payment_invoice = self._combo(form, "Hóa đơn", ["Chọn hóa đơn"])
        self._payment_date = self._entry(form, "Ngày thanh toán", "2026-07-22")
        self._payment_amount = self._entry(form, "Số tiền", "500000")
        self._payment_method = self._combo(form, "Phương thức", list(finance_service.PAYMENT_METHODS))
        self._transaction_ref = self._entry(form, "Mã giao dịch/chứng từ")
        ctk.CTkButton(form, text="Ghi nhận thanh toán", command=self._save_payment, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa thanh toán đang chọn", command=self._delete_selected_payment, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._payment_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._payment_table = DataTable(
            table_area,
            columns=[("id", "Mã", 85), ("invoice", "Hóa đơn", 90), ("date", "Ngày", 100), ("amount", "Số tiền", 100), ("method", "Phương thức", 120), ("ref", "Chứng từ", 120)],
        )
        self._payment_table.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        self._debt_table = DataTable(
            table_area,
            columns=[("id", "Hóa đơn", 90), ("student", "HS", 80), ("term", "Kỳ", 100), ("remain", "Còn nợ", 100), ("due", "Hạn", 100), ("status", "Trạng thái", 130)],
        )
        self._debt_table.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    def _build_scholarship_tab(self) -> None:
        self._scholarship_tab.grid_columnconfigure(0, weight=0, minsize=330)
        self._scholarship_tab.grid_columnconfigure(1, weight=1)
        self._scholarship_tab.grid_rowconfigure(0, weight=1)
        form_card = card(self._scholarship_tab, width=330)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._scholarship_term = self._entry(form, "Kỳ xét học bổng", "HK1 2026")
        self._min_gpa = self._entry(form, "GPA tối thiểu", "3.2")
        self._scholarship_amount = self._entry(form, "Mức học bổng", "1000000")
        self._conduct_score = self._entry(form, "Điểm rèn luyện tối thiểu", "90")
        ctk.CTkButton(form, text="Quét đề xuất học bổng", command=self._scan_scholarships, **primary_button_kwargs()).pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(form, text="Xóa học bổng đang chọn", command=self._delete_selected_scholarship, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_area = card(self._scholarship_tab)
        table_area.grid(row=0, column=1, sticky="nsew", pady=10)
        self._scholarship_table = DataTable(
            table_area,
            columns=[("id", "Mã", 120), ("student", "HS", 80), ("term", "Kỳ", 100), ("gpa", "GPA", 70), ("avg", "TB10", 70), ("conduct", "Rèn luyện", 90), ("amount", "Tiền", 100), ("status", "Trạng thái", 100)],
        )
        self._scholarship_table.pack(fill="both", expand=True, padx=10, pady=10)

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

    def _refresh_options(self) -> None:
        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        student_values = ["Chọn học sinh"] + list(self._students.keys())
        self._invoice_student.configure(values=student_values)
        if self._invoice_student.get() not in student_values:
            self._invoice_student.set(student_values[0])

        invoices = finance_service.list_invoices()
        self._invoices = {f"{i.invoice_id} - {i.ma_hs}": i.invoice_id for i in invoices}
        invoice_values = ["Chọn hóa đơn"] + list(self._invoices.keys())
        self._payment_invoice.configure(values=invoice_values)
        if self._payment_invoice.get() not in invoice_values:
            self._payment_invoice.set(invoice_values[0])

    def _save_invoice(self) -> None:
        try:
            credit_text = self._credit_count.get().strip()
            invoice = TuitionInvoiceInfo(
                invoice_id=self._invoice_id.get().strip(),
                ma_hs=self._code(self._students, self._invoice_student.get()) or "",
                term=self._term.get().strip(),
                invoice_type=self._invoice_type.get().strip(),
                credit_count=int(credit_text) if credit_text else None,
                unit_price=float(self._unit_price.get().strip() or 0),
                fixed_amount=float(self._fixed_amount.get().strip() or 0),
                due_date=self._due_date.get().strip() or None,
            )
            finance_service.create_invoice(invoice)
            messagebox.showinfo("Thành công", "Đã lập hóa đơn học phí.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _save_payment(self) -> None:
        try:
            payment = PaymentRecordInfo(
                payment_id=self._payment_id.get().strip(),
                invoice_id=self._code(self._invoices, self._payment_invoice.get()) or "",
                payment_date=self._payment_date.get().strip(),
                amount=float(self._payment_amount.get().strip()),
                method=self._payment_method.get().strip(),
                transaction_ref=self._transaction_ref.get().strip() or None,
            )
            finance_service.record_payment(payment)
            messagebox.showinfo("Thành công", "Đã ghi nhận thanh toán.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _scan_scholarships(self) -> None:
        try:
            count = finance_service.scan_scholarships(
                self._scholarship_term.get().strip(),
                min_gpa4=float(self._min_gpa.get().strip()),
                amount=float(self._scholarship_amount.get().strip()),
                conduct_score=float(self._conduct_score.get().strip()),
            )
            messagebox.showinfo("Thành công", f"Đã tạo/cập nhật {count} đề xuất học bổng.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))


    def _selected_table_id(self, table, empty_message: str):
        values = table.get_selected_values()
        if not values:
            messagebox.showwarning("Cảnh báo", empty_message)
            return None
        return values[0]

    def _delete_selected_invoice(self):
        invoice_id = self._selected_table_id(self._invoice_table, "Vui lòng chọn hóa đơn cần xóa.")
        if invoice_id and messagebox.askyesno("Xác nhận", f"Xóa hóa đơn {invoice_id}?"):
            finance_service.delete_invoice(invoice_id)
            self.refresh()

    def _delete_selected_payment(self):
        payment_id = self._selected_table_id(self._payment_table, "Vui lòng chọn thanh toán cần xóa.")
        if payment_id and messagebox.askyesno("Xác nhận", f"Xóa thanh toán {payment_id}?"):
            finance_service.delete_payment(payment_id)
            self.refresh()

    def _delete_selected_scholarship(self):
        scholarship_id = self._selected_table_id(self._scholarship_table, "Vui lòng chọn học bổng cần xóa.")
        if scholarship_id and messagebox.askyesno("Xác nhận", f"Xóa học bổng {scholarship_id}?"):
            finance_service.delete_scholarship(scholarship_id)
            self.refresh()

    def _invoice_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values and messagebox.askyesno("Xác nhận", f"Xóa hóa đơn {values[0]}?"):
            finance_service.delete_invoice(values[0])
            self.refresh()

    def _payment_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values:
            finance_service.delete_payment(values[0])
            self.refresh()

    def _scholarship_action(self, action: str, values: tuple) -> None:
        if action == "delete" and values:
            finance_service.delete_scholarship(values[0])
            self.refresh()

    def _render_tables(self) -> None:
        invoices = finance_service.list_invoices()
        self._invoice_table.load([
            (i.invoice_id, i.ma_hs, i.term, i.invoice_type, f"{i.total_amount:g}", f"{i.paid_amount:g}", i.status)
            for i in invoices
        ])
        self._payment_table.load([
            (p.payment_id, p.invoice_id, p.payment_date, f"{p.amount:g}", p.method, p.transaction_ref or "")
            for p in finance_service.list_payments()
        ])
        self._debt_table.load([
            (i.invoice_id, i.ma_hs, i.term, f"{max(0, i.total_amount - i.paid_amount):g}", i.due_date or "", i.status)
            for i in finance_service.list_debts()
        ])
        self._scholarship_table.load([
            (s.scholarship_id, s.ma_hs, s.term, s.gpa4 or "", s.average10 or "", s.conduct_score or "", s.amount or "", s.status)
            for s in finance_service.list_scholarships()
        ])

    def refresh(self) -> None:
        self._refresh_options()
        summary = finance_service.summary()
        for key, value in summary.items():
            if key in self._metrics:
                self._metrics[key].set_value(str(value))
        self._render_tables()
        self._set_entry(self._invoice_id, finance_service.next_invoice_id())
        self._set_entry(self._payment_id, finance_service.next_payment_id())
