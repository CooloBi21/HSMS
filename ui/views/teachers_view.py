import customtkinter as ctk
from tkinter import messagebox

from models.teacher import GiaoVienInfo
from services import teacher_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading
from utils.labels import STATUS_FILTER_VI, teacher_status_db, teacher_status_vi

_STATUS_OPTIONS = ["Chọn trạng thái", "Đang giảng dạy", "Tạm nghỉ"]
_STATUS_TO_DB = {"Đang giảng dạy": "Active", "Tạm nghỉ": "Inactive"}
_STATUS_FROM_DB = {v: k for k, v in _STATUS_TO_DB.items()}
_SUBJECT_OPTIONS = ["Chọn môn phụ trách", "Toán", "Ngữ Văn", "Tiếng Anh", "Vật lý", "Hóa học", "Sinh học", "Lịch sử", "Địa lý", "Tin học"]
_SUBJECT_FILTER_OPTIONS = ["Tất cả môn"] + _SUBJECT_OPTIONS[1:]


class TeachersView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._editing_id: str | None = None
        self._all_rows: list = []
        self._teacher_kpis: dict = {}
        self._pagination = None
        self._pending_new: bool = False
        self._build()

    def _build(self) -> None:
        heading(self, "Quản lý Giáo viên", size=26).pack(anchor="w", padx=4)
        subheading(self, "Thêm, sửa, xóa hồ sơ giáo viên và theo dõi trạng thái giảng dạy.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate([
            ("total", "Tổng GV", "#2563eb", "Đang quản lý", "GV"),
            ("active", "Đang dạy", "#10b981", "Đang giảng dạy", "ON"),
            ("inactive", "Tạm nghỉ", "#f59e0b", "Cần theo dõi", "!"),
            ("subjects", "Số môn", "#7c3aed", "Phụ trách", "M"),
        ]):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._teacher_kpis[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=360)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form_card = card(body, width=360)
        form_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        form_scroll = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(form_scroll, text="Hồ sơ giáo viên", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=4, pady=(8, 8)
        )
        # TeacherID ẩn khỏi form — tự sinh từ TeacherCode khi thêm mới
        ctk.CTkLabel(form_scroll, text="Mã số giáo viên", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        self._teacher_code = ctk.CTkEntry(form_scroll, placeholder_text="Tự động sinh", state="disabled", height=40)
        self._teacher_code.pack(fill="x", pady=(2, 0))
        self._full_name = self._field(form_scroll, "Họ tên")
        self._gender = self._combo(form_scroll, "Giới tính", ["Chọn giới tính", "Nam", "Nữ"])
        self._dob = self._field(form_scroll, "Ngày sinh (YYYY-MM-DD)")
        self._phone = self._field(form_scroll, "Điện thoại")
        self._email = self._field(form_scroll, "Email")
        self._address = self._field(form_scroll, "Địa chỉ")
        self._subject = self._combo(form_scroll, "Môn phụ trách", _SUBJECT_OPTIONS)
        self._status = self._combo(form_scroll, "Trạng thái", _STATUS_OPTIONS)

        self._save_btn = build_form_actions(
            form_card,
            self._save,
            self._reset,
            self._delete,
            save_text="Lưu giáo viên",
            reset_text="Làm mới form",
            delete_text="Xóa giáo viên đã chọn",
        )

        list_card = card(body)
        list_card.grid(row=0, column=1, sticky="nsew")

        toolbar = ctk.CTkFrame(list_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=10)
        self._search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã giáo viên hoặc họ tên...", height=38)
        self._search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._search.bind("<KeyRelease>", lambda _e: self._on_filter_change())
        self._subject_filter = ctk.CTkComboBox(
            toolbar, values=_SUBJECT_FILTER_OPTIONS, width=150, height=38, command=lambda _v: self._on_filter_change()
        )
        self._subject_filter.pack(side="left", padx=(0, 8))
        self._subject_filter.set("Tất cả môn")
        self._status_filter = ctk.CTkComboBox(
            toolbar, values=["Tất cả trạng thái", "Đang giảng dạy", "Tạm nghỉ"], width=170, height=38, command=lambda _v: self._on_filter_change()
        )
        self._status_filter.pack(side="left", padx=(0, 8))
        self._status_filter.set("Tất cả trạng thái")
        ctk.CTkButton(
            toolbar,
            text="+ Thêm giáo viên",
            height=38,
            corner_radius=10,
            command=self._on_new_clicked,
            **primary_button_kwargs(),
        ).pack(side="left")

        self._table = DataTable(
            list_card,
            columns=[
                ("code", "Mã GV", 80), ("name", "Họ tên", 150), ("gender", "GT", 70),
                ("subject", "Môn", 95), ("phone", "Điện thoại", 105), ("status", "Trạng thái", 130),
            ],
            on_select=self._on_row_select,
        )
        self._table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._empty_label = ctk.CTkLabel(
            list_card,
            text="Không tìm thấy giáo viên phù hợp. Hãy thử đổi từ khóa hoặc bộ lọc.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )

        self._pagination = PaginationBar(list_card, on_change=self._render_page, page_size=8)
        self._pagination.pack(fill="x", padx=10, pady=(0, 10))

        if self._on_navigate:
            ScreenNavBar(self, "teachers", self._on_navigate).pack(fill="x", pady=(4, 0))

        self._fill_next_code()

    def _field(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=40)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=40)
        if values:
            combo.set(values[0])
        combo.pack(fill="x", pady=(2, 0))
        return combo

    def _on_filter_change(self) -> None:
        self._pagination.reset()
        self.refresh()

    def _gender_to_int(self, text: str) -> int | None:
        return 1 if text == "Nam" else 0 if text == "Nữ" else None

    def _format_gender(self, gender_text: str) -> str:
        if gender_text == "Nam":
            return "[Nam]"
        if gender_text == "Nữ":
            return "[Nữ]"
        return "[Khác]"

    def _format_subject(self, subject: str | None) -> str:
        return f"[{subject}]" if subject else "[Chưa có môn]"

    def _format_status(self, status: str | None) -> str:
        return f"[{teacher_status_vi(status)}]"

    def _update_kpis(self, teachers: list) -> None:
        active = len([t for t in teachers if t.status == "Active"])
        inactive = len([t for t in teachers if t.status == "Inactive"])
        subjects = len({t.subject for t in teachers if t.subject})
        self._teacher_kpis["total"].set_value(str(len(teachers)))
        self._teacher_kpis["active"].set_value(str(active))
        self._teacher_kpis["inactive"].set_value(str(inactive))
        self._teacher_kpis["subjects"].set_value(str(subjects))

    def _auto_teacher_id(self, teacher_code: str) -> str:
        """Tự động sinh TeacherID từ TeacherCode (thêm tiền tố T_)."""
        return f"T_{teacher_code}" if teacher_code else ""

    def _set_teacher_code(self, teacher_code: str) -> None:
        self._teacher_code.configure(state="normal")
        self._teacher_code.delete(0, "end")
        self._teacher_code.insert(0, teacher_code)
        self._teacher_code.configure(state="disabled")

    def _get_teacher_code(self) -> str:
        self._teacher_code.configure(state="normal")
        teacher_code = self._teacher_code.get().strip()
        self._teacher_code.configure(state="disabled")
        return teacher_code

    def _fill_next_code(self) -> None:
        self._set_teacher_code(teacher_service.generate_next_code())

    def _clear_other_fields(self) -> None:
        for w in (self._full_name, self._dob, self._phone, self._email, self._address):
            w.configure(state="normal")
            w.delete(0, "end")
        self._gender.set("Chọn giới tính")
        self._subject.set("Chọn môn phụ trách")
        self._status.set("Đang giảng dạy")

    def _form_to_model(self) -> GiaoVienInfo:
        status_label = self._status.get()
        teacher_code = self._get_teacher_code()
        # Khi thêm mới: tự sinh teacher_id; khi cập nhật: dùng editing_id hiện tại
        teacher_id = self._editing_id if self._editing_id else self._auto_teacher_id(teacher_code)
        return GiaoVienInfo(
            teacher_id=teacher_id,
            teacher_code=teacher_code,
            full_name=self._full_name.get().strip(),
            gender=self._gender_to_int(self._gender.get()),
            dob=self._dob.get().strip() or None,
            phone=self._phone.get().strip() or None,
            email=self._email.get().strip() or None,
            address=self._address.get().strip() or None,
            subject=None if self._subject.get() == "Chọn môn phụ trách" else self._subject.get().strip(),
            status=_STATUS_TO_DB.get(status_label, "Active"),
        )

    def _fill_form(self, gv: GiaoVienInfo) -> None:
        self._editing_id = gv.teacher_id
        self._pending_new = False
        for entry, val in [
            (self._teacher_code, gv.teacher_code), (self._full_name, gv.full_name),
            (self._dob, gv.dob or ""), (self._phone, gv.phone or ""),
            (self._email, gv.email or ""), (self._address, gv.address or ""),
        ]:
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, val)
        # Mã số giáo viên không cho sửa khi đang chỉnh sửa hồ sơ
        self._teacher_code.configure(state="disabled")
        self._gender.set(gv.gioi_tinh_text or "Chọn giới tính")
        self._subject.set(gv.subject or "Chọn môn phụ trách")
        self._status.set(_STATUS_FROM_DB.get(gv.status or "Active", "Đang giảng dạy"))
        self._save_btn.configure(text="Cập nhật giáo viên")

    def _reset(self) -> None:
        self._editing_id = None
        self._pending_new = False
        self._fill_next_code()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu giáo viên")

    def _on_new_clicked(self) -> None:
        if self._pending_new:
            messagebox.showwarning(
                "Đang thêm mới",
                "Ban Đang thêm mới giáo viên. Vui lòng lưu hoặc chọn một giáo viên khác trước khi thêm mới tiếp.",
            )
            return

        self._editing_id = None
        self._pending_new = True
        self._fill_next_code()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu giáo viên")

    def _on_row_select(self, values: tuple) -> None:
        gv = teacher_service.get_teacher_by_code(values[0])
        if gv:
            self._fill_form(gv)

    def _on_table_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        teacher_code = values[0]
        gv = teacher_service.get_teacher_by_code(teacher_code)
        if not gv:
            return
        if action == "edit":
            self._fill_form(gv)
            return
        if action == "delete":
            self._delete_teacher_by_id(gv.teacher_id)
            return
        if action == "detail":
            messagebox.showinfo(
                "Chi tiết giáo viên",
                f"{gv.teacher_code} - {gv.full_name}\n"
                f"Môn: {gv.subject or 'Chưa có môn'}\n"
                f"Điện thoại: {gv.phone or 'Chưa có'}\n"
                f"Email: {gv.email or 'Chưa có'}\n"
                f"Trạng thái: {teacher_status_vi(gv.status)}",
            )

    def _save(self) -> None:
        try:
            gv = self._form_to_model()
            if self._editing_id:
                gv.teacher_id = self._editing_id
                teacher_service.update_teacher(gv)
                messagebox.showinfo("Thành công", "Đã cập nhật giáo viên.")
            else:
                teacher_service.create_teacher(gv)
                messagebox.showinfo("Thành công", "Đã thêm giáo viên mới.")
            self._pending_new = False
            self._notify()
            self._reset()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete(self) -> None:
        if not self._editing_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giáo viên cần xóa từ danh sách.")
            return
        self._delete_teacher_by_id(self._editing_id)
        return

    def _delete_teacher_by_id(self, teacher_id: str) -> None:
        gv = teacher_service.get_teacher(teacher_id)
        name = gv.full_name if gv else teacher_id
        if not messagebox.askyesno("Xác nhận", f"Xóa giáo viên {name}?"):
            return
        try:
            teacher_service.delete_teacher(teacher_id)
            messagebox.showinfo("Thành công", "Đã xóa giáo viên.")
            self._notify()
            self._reset()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _render_page(self) -> None:
        page_rows = self._pagination.slice(self._all_rows)
        self._table.load(page_rows)
        if page_rows:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(fill="x", padx=16, pady=(2, 10))

    def refresh(self) -> None:
        search = self._search.get().strip() or None
        status_label = self._status_filter.get()
        status = None if status_label == "Tất cả trạng thái" else teacher_status_db(status_label)
        teachers = teacher_service.list_teachers(search=search, status=status)
        all_teachers = teacher_service.list_teachers()
        self._update_kpis(all_teachers)
        subject_filter = self._subject_filter.get()
        if subject_filter != "Tất cả môn":
            teachers = [t for t in teachers if t.subject == subject_filter]
        self._all_rows = [
            (
                t.teacher_code,
                t.full_name,
                self._format_gender(t.gioi_tinh_text),
                self._format_subject(t.subject),
                t.phone or "",
                self._format_status(t.status),
                "Sửa | Chi tiết | Xóa",
            )
            for t in teachers
        ]
        self._render_page()
