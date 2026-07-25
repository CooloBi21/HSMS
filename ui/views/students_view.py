import customtkinter as ctk
from tkinter import messagebox

from models.student import HocSinhInfo
from services import student_service, school_class_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading


class StudentsView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._editing_id: str | None = None
        self._class_map: dict = {}
        self._all_rows: list = []
        self._student_kpis: dict = {}
        self._pagination = None
        self._pending_new: bool = False  # True khi đang ở chế độ thêm mới nhưng chưa lưu
        self._build()

    def _build(self) -> None:
        heading(self, "Quản lý Học sinh", size=26).pack(anchor="w", padx=4)
        subheading(self, "Thêm, sửa, xóa và lọc danh sách học sinh theo lớp.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate([
            ("total", "Tổng HS", "#2563eb", "Đang quản lý", "HS"),
            ("avg", "Điểm TB", "#10b981", "Toàn trường", "TB"),
            ("low", "HS dưới 5", "#ef4444", "Cần theo dõi", "!"),
            ("classes", "Lớp có HS", "#7c3aed", "Có học sinh", "L"),
        ]):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._student_kpis[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=360)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form_card = card(body, width=360)
        form_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        form_scroll = ctk.CTkScrollableFrame(form_card, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(form_scroll, text="Hồ sơ học sinh", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=4, pady=(8, 8)
        )
        # Mã học sinh luôn ở trạng thái chỉ đọc — được sinh tự động
        ctk.CTkLabel(form_scroll, text="Mã học sinh", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        self._ma_hs = ctk.CTkEntry(form_scroll, placeholder_text="Tự động sinh", state="disabled", height=40)
        self._ma_hs.pack(fill="x", pady=(2, 0))

        self._ho_ten = self._field(form_scroll, "Họ tên")
        self._gioi_tinh = self._combo(form_scroll, "Giới tính", ["", "Nam", "Nữ"])
        self._ngay_sinh = self._field(form_scroll, "Ngày sinh (YYYY-MM-DD)")
        self._dia_chi = self._field(form_scroll, "Địa chỉ")
        self._diem_tb = self._field(form_scroll, "Điểm TB")
        self._ma_lop = self._combo(form_scroll, "Lớp", [])

        self._save_btn = build_form_actions(
            form_card,
            self._save,
            self._reset_form,
            self._delete,
            save_text="Lưu học sinh",
            reset_text="Làm mới form",
            delete_text="Xóa học sinh đã chọn",
        )

        list_card = card(body)
        list_card.grid(row=0, column=1, sticky="nsew")

        toolbar = ctk.CTkFrame(list_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=10)
        self._search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã học sinh hoặc họ tên...", height=38)
        self._search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._search.bind("<KeyRelease>", lambda _e: self._on_filter_change())
        self._filter_lop = ctk.CTkComboBox(toolbar, values=["Tất cả lớp"], width=180, height=38, command=lambda _v: self._on_filter_change())
        self._filter_lop.pack(side="left", padx=(0, 8))
        self._filter_lop.set("Tất cả lớp")
        ctk.CTkButton(
            toolbar,
            text="+ Thêm học sinh",
            height=38,
            corner_radius=10,
            command=self._on_new_clicked,
            **primary_button_kwargs(),
        ).pack(side="left")

        self._table = DataTable(
            list_card,
            columns=[
                ("ma_hs", "Mã HS", 80), ("ho_ten", "Họ tên", 150), ("gioi_tinh", "GT", 70),
                ("ngay_sinh", "Ngày sinh", 100), ("diem_tb", "Điểm TB", 80), ("lop", "Lớp", 120),
            ],
            on_select=self._on_row_select,
        )
        self._table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._empty_label = ctk.CTkLabel(
            list_card,
            text="Không tìm thấy học sinh phù hợp. Hãy thử đổi từ khóa hoặc bộ lọc lớp.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )

        self._pagination = PaginationBar(list_card, on_change=self._render_page, page_size=8)
        self._pagination.pack(fill="x", padx=10, pady=(0, 10))

        if self._on_navigate:
            ScreenNavBar(self, "students", self._on_navigate).pack(fill="x", pady=(4, 0))

        # Điền sẵn mã mới khi khởi tạo
        self._fill_next_id()

    # ─── helpers ────────────────────────────────────────────────────────────

    def _field(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=40)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(6, 0))
        combo_values = values or ["Chọn lớp"]
        combo = ctk.CTkComboBox(parent, values=combo_values, height=40)
        if not values:
            combo.set("Chọn lớp")
        combo.pack(fill="x", pady=(2, 0))
        return combo

    def _fill_next_id(self) -> None:
        """Điền sẵn mã học sinh tiếp theo vào ô mã (chỉ đọc)."""
        next_id = student_service.generate_next_id()
        self._ma_hs.configure(state="normal")
        self._ma_hs.delete(0, "end")
        self._ma_hs.insert(0, next_id)
        self._ma_hs.configure(state="disabled")

    def _has_partial_data(self) -> bool:
        """Kiểm tra xem người dùng đã nhập gì chưa (tránh cảnh báo thừa khi form trống)."""
        return any([
            self._ho_ten.get().strip(),
            self._ngay_sinh.get().strip(),
            self._dia_chi.get().strip(),
            self._diem_tb.get().strip(),
        ])

    def _on_filter_change(self) -> None:
        self._pagination.reset()
        self.refresh()

    def _load_class_options(self) -> None:
        classes = school_class_service.list_classes()
        self._class_map = {f"{c.ten_lop} ({c.ma_lop})": c.ma_lop for c in classes}
        lop_values = list(self._class_map.keys())
        self._ma_lop.configure(values=lop_values)
        self._filter_lop.configure(values=["Tất cả lớp"] + lop_values)
        if self._ma_lop.get() not in lop_values:
            self._ma_lop.set("Chọn lớp")

    def _get_selected_lop(self) -> str | None:
        return self._class_map.get(self._ma_lop.get())

    def _gender_to_int(self, text: str) -> int | None:
        return 1 if text == "Nam" else 0 if text in ("Nữ", "Nu") else None

    def _form_to_model(self) -> HocSinhInfo:
        diem = self._diem_tb.get().strip()
        # Đọc mã từ ô bị disabled: cần enable tạm thời
        self._ma_hs.configure(state="normal")
        ma_hs_val = self._ma_hs.get().strip()
        self._ma_hs.configure(state="disabled")
        return HocSinhInfo(
            ma_hs=ma_hs_val,
            ho_ten=self._ho_ten.get().strip(),
            gioi_tinh=self._gender_to_int(self._gioi_tinh.get()),
            ngay_sinh=self._ngay_sinh.get().strip() or None,
            dia_chi=self._dia_chi.get().strip() or None,
            diem_tb=float(diem) if diem else None,
            ma_lop=self._get_selected_lop(),
        )

    def _fill_form(self, hs: HocSinhInfo) -> None:
        """Điền form khi chọn một học sinh để sửa."""
        self._editing_id = hs.ma_hs
        self._pending_new = False
        self._ma_hs.configure(state="normal")
        self._ma_hs.delete(0, "end")
        self._ma_hs.insert(0, hs.ma_hs)
        self._ma_hs.configure(state="disabled")
        self._ho_ten.delete(0, "end")
        self._ho_ten.insert(0, hs.ho_ten)
        self._gioi_tinh.set(hs.gioi_tinh_text or "")
        self._ngay_sinh.delete(0, "end")
        self._ngay_sinh.insert(0, hs.ngay_sinh or "")
        self._dia_chi.delete(0, "end")
        self._dia_chi.insert(0, hs.dia_chi or "")
        self._diem_tb.delete(0, "end")
        self._diem_tb.insert(0, str(hs.diem_tb) if hs.diem_tb is not None else "")
        for label, code in self._class_map.items():
            if code == hs.ma_lop:
                self._ma_lop.set(label)
                break
        self._save_btn.configure(text="Cập nhật học sinh")

    def _clear_other_fields(self) -> None:
        """Xóa các trường nhập liệu (trừ mã HS)."""
        for w in (self._ho_ten, self._ngay_sinh, self._dia_chi, self._diem_tb):
            w.delete(0, "end")
        self._gioi_tinh.set("")
        if self._class_map:
            self._ma_lop.set(list(self._class_map.keys())[0])

    # ─── actions ────────────────────────────────────────────────────────────

    def _reset_form(self) -> None:
        self._editing_id = None
        self._pending_new = False
        self._fill_next_id()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu học sinh")

    def _on_new_clicked(self) -> None:
        if self._pending_new:
            messagebox.showwarning(
                "Đang thêm mới",
                "Ban Đang thêm mới học sinh. Vui lòng lưu hoặc chọn một học sinh khác trước khi thêm mới tiếp.",
            )
            return

        """Xử lý khi người dùng bấm nút 'Thêm mới'."""
        if self._pending_new and self._has_partial_data():
            # Người dùng đang nhập dở — hỏi xác nhận
            confirmed = messagebox.askyesno(
                "Xác nhận",
                "Bạn đang có thông tin chưa được lưu.\n"
                "Nếu tiếp tục, toàn bộ dữ liệu đang nhập sẽ bị xóa.\n\n"
                "Bạn có chắc muốn tạo hồ sơ mới không?",
            )
            if not confirmed:
                return

        # Chuyển sang chế độ thêm mới
        self._editing_id = None
        self._pending_new = True
        self._fill_next_id()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu học sinh")

    def _on_row_select(self, values: tuple) -> None:
        hs = student_service.get_student(values[0])
        if hs:
            self._fill_form(hs)

    def _on_table_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        ma_hs = values[0]
        if action == "edit":
            hs = student_service.get_student(ma_hs)
            if hs:
                self._fill_form(hs)
            return
        if action == "delete":
            self._delete_student_by_id(ma_hs)

    def _save(self) -> None:
        try:
            hs = self._form_to_model()
            if self._editing_id:
                hs.ma_hs = self._editing_id
                student_service.update_student(hs)
                messagebox.showinfo("Thành công", "Đã cập nhật học sinh.")
            else:
                student_service.create_student(hs)
                messagebox.showinfo("Thành công", "Đã thêm học sinh mới.")
            self._pending_new = False
            self._editing_id = None
            self._notify()
            self.refresh()
            # Sau khi lưu: điền sẵn mã mới tiếp theo
            self._fill_next_id()
            self._clear_other_fields()
            self._save_btn.configure(text="Lưu học sinh")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete(self) -> None:
        if not self._editing_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn học sinh cần xóa từ danh sách.")
            return
        self._delete_student_by_id(self._editing_id)

    def _delete_student_by_id(self, ma_hs: str) -> None:
        hs = student_service.get_student(ma_hs)
        name = hs.ho_ten if hs else ma_hs
        if not messagebox.askyesno("Xác nhận", f"Xóa học sinh {name}?"):
            return
        try:
            student_service.delete_student(ma_hs)
            messagebox.showinfo("Thành công", "Đã xóa học sinh.")
            self._pending_new = False
            self._editing_id = None
            self._notify()
            self.refresh()
            self._fill_next_id()
            self._clear_other_fields()
            self._save_btn.configure(text="Lưu học sinh")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _format_gender(self, gender_text: str) -> str:
        if gender_text == "Nam":
            return "[Nam]"
        if gender_text in ("Nữ", "Nu"):
            return "[Nữ]"
        return "[Khác]"

    def _format_score(self, score) -> str:
        if score in ("", None):
            return "Chưa có"
        value = float(score)
        if value < 5:
            return f"{value:g} · Cần theo dõi"
        if value < 6.5:
            return f"{value:g} · TB"
        if value < 8:
            return f"{value:g} · Khá"
        return f"{value:g} · Tốt"

    def _update_kpis(self, students: list) -> None:
        scores = [s.diem_tb for s in students if s.diem_tb is not None]
        avg = round(sum(scores) / len(scores), 2) if scores else 0
        low = len([s for s in students if s.diem_tb is not None and s.diem_tb < 5])
        classes_with_students = len({s.ma_lop for s in students if s.ma_lop})
        self._student_kpis["total"].set_value(str(len(students)))
        self._student_kpis["avg"].set_value(str(avg))
        self._student_kpis["low"].set_value(str(low))
        self._student_kpis["classes"].set_value(str(classes_with_students))

    def _render_page(self) -> None:
        page_rows = self._pagination.slice(self._all_rows)
        self._table.load(page_rows)
        if page_rows:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(fill="x", padx=16, pady=(2, 10))

    def refresh(self) -> None:
        self._load_class_options()
        all_students = student_service.list_students()
        self._update_kpis(all_students)
        search = self._search.get().strip() or None
        filter_label = self._filter_lop.get()
        ma_lop = None if filter_label == "Tất cả lớp" else self._class_map.get(filter_label)
        students = student_service.list_students(ma_lop=ma_lop, search=search)
        lop_names = {c.ma_lop: c.ten_lop for c in school_class_service.list_classes()}
        self._all_rows = [
            (
                s.ma_hs,
                s.ho_ten,
                self._format_gender(s.gioi_tinh_text),
                s.ngay_sinh or "",
                self._format_score(s.diem_tb),
                lop_names.get(s.ma_lop, ""),
                "Sửa  |  Xóa",
            )
            for s in students
        ]
        self._render_page()
