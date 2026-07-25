import customtkinter as ctk
from tkinter import messagebox

from services import account_service, student_service
from ui.components.data_table import DataTable
from ui.components.metric_card import MetricCard
from ui.components.screen_nav import ScreenNavBar
from ui.theme import card, heading, primary_button_kwargs, subheading


class AccountsView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._students = {}
        self._metrics = {}
        self._build()

    def _build(self):
        heading(self, "Tài khoản người dùng", size=26).pack(anchor="w", padx=4)
        subheading(self, "Tạo tài khoản riêng cho học sinh để chuẩn bị cho đăng ký học phần tự phục vụ.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi = ctk.CTkFrame(self, fg_color="transparent")
        kpi.pack(fill="x", pady=(0, 12))
        for i in range(3):
            kpi.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate([
            ("total", "Tổng tài khoản", "#2563eb", "Đã tạo", "TK"),
            ("students", "Học sinh", "#10b981", "Vai trò Student", "HS"),
            ("locked", "Bị khóa", "#ef4444", "Không hoạt động", "!"),
        ]):
            metric = MetricCard(kpi, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=360)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form_card = card(body, width=360)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        form = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)
        self._account_id = self._entry(form, "Mã tài khoản", account_service.next_account_id())
        self._student = self._combo(form, "Học sinh", ["Chọn học sinh"])
        self._username = self._entry(form, "Tên đăng nhập")
        self._password = self._entry(form, "Mật khẩu mặc định")
        ctk.CTkButton(form, text="Tạo tài khoản học sinh", height=40, command=self._create_student_account, **primary_button_kwargs()).pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(form, text="Khóa tài khoản học sinh", height=40, command=self._lock_selected_account, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(form, text="Xóa tài khoản học sinh", height=40, command=self._delete_selected_account, **primary_button_kwargs()).pack(fill="x", padx=12, pady=(0, 12))

        table_card = card(body)
        table_card.grid(row=0, column=1, sticky="nsew")
        self._table = DataTable(
            table_card,
            columns=[("id", "Mã", 90), ("username", "Tên đăng nhập", 150), ("role", "Vai trò", 90), ("student", "Mã HS", 80), ("status", "Trạng thái", 100)],
        )
        self._table.pack(fill="both", expand=True, padx=10, pady=10)

        if self._on_navigate:
            ScreenNavBar(self, "accounts", self._on_navigate).pack(fill="x", pady=(8, 0))

    def _entry(self, parent, label, value=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(8, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=38)
        entry.insert(0, value)
        entry.pack(fill="x", padx=12, pady=(2, 0))
        return entry

    def _combo(self, parent, label, values):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(8, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=38)
        combo.set(values[0])
        combo.pack(fill="x", padx=12, pady=(2, 0))
        return combo

    def _set_entry(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def _refresh_students(self):
        students = student_service.list_students()
        self._students = {f"{s.ho_ten} ({s.ma_hs})": s.ma_hs for s in students}
        values = ["Chọn học sinh"] + list(self._students.keys())
        self._student.configure(values=values)
        if self._student.get() not in values:
            self._student.set(values[0])

    def _create_student_account(self):
        try:
            account_service.create_student_account(
                self._account_id.get().strip(),
                self._students.get(self._student.get(), ""),
                self._username.get().strip(),
                self._password.get(),
            )
            messagebox.showinfo("Thành công", "Đã tạo tài khoản học sinh.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _account_action(self, action, values):
        if not values:
            return
        account_id = values[0]
        try:
            if action == "lock":
                account_service.set_status(account_id, "Locked")
            elif action == "unlock":
                account_service.set_status(account_id, "Active")
            elif action == "delete":
                account_service.delete_account(account_id)
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _selected_account_id(self):
        values = self._table.get_selected_values()
        if not values:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản học sinh cần thao tác.")
            return None
        return values[0]

    def _lock_selected_account(self):
        account_id = self._selected_account_id()
        if not account_id:
            return
        try:
            account_service.set_status(account_id, "Locked")
            messagebox.showinfo("Thành công", "Đã khóa tài khoản học sinh.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete_selected_account(self):
        account_id = self._selected_account_id()
        if not account_id:
            return
        if not messagebox.askyesno("Xác nhận", f"Xóa tài khoản {account_id}?"):
            return
        try:
            account_service.delete_account(account_id)
            messagebox.showinfo("Thành công", "Đã xóa tài khoản học sinh.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def refresh(self):
        self._refresh_students()
        accounts = account_service.list_accounts()
        self._metrics["total"].set_value(str(len(accounts)))
        self._metrics["students"].set_value(str(len([a for a in accounts if a.role == "Student"])))
        self._metrics["locked"].set_value(str(len([a for a in accounts if a.status == "Locked"])))
        self._table.load([(a.account_id, a.username, a.role, a.ma_hs or "", a.status, "Khóa | Mở | Xóa") for a in accounts])
        self._set_entry(self._account_id, account_service.next_account_id())
