import customtkinter as ctk
from tkinter import messagebox

from models.school_class import LopInfo
from services import school_class_service
from ui.components.data_table import DataTable
from ui.components.form_buttons import build_form_actions
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import TEXT_MUTED, card, heading, primary_button_kwargs, subheading


class ClassesView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_data_changed = on_data_changed
        self._on_navigate = on_navigate
        self._editing_id: str | None = None
        self._all_rows: list = []
        self._class_kpis: dict = {}
        self._pagination = None
        self._pending_new: bool = False
        self._build()

    def _build(self) -> None:
        heading(self, "Quản lý Lớp học", size=26).pack(anchor="w", padx=4)
        subheading(self, "Thêm, sửa, xóa lớp và theo dõi sĩ số từng lớp học.").pack(anchor="w", padx=4, pady=(2, 12))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)
        for i, (key, title, accent, subtitle, icon) in enumerate([
            ("classes", "Tổng lớp", "#2563eb", "Đang quản lý", "L"),
            ("students", "Tổng HS", "#10b981", "Trong các lớp", "HS"),
            ("empty", "Lớp trống", "#f59e0b", "Chưa có HS", "!"),
            ("largest", "Lớp đông nhất", "#7c3aed", "Theo sĩ số", "TOP"),
        ]):
            metric = MetricCard(kpi_row, title, "0", accent=accent, subtitle=subtitle, icon=icon)
            metric.grid(row=0, column=i, padx=5, sticky="nsew")
            self._class_kpis[key] = metric

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0, minsize=340)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        form_card = card(body, width=340)
        form_card.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="both", expand=True)

        ctk.CTkLabel(form_inner, text="Thông tin lớp", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 8)
        )
        ctk.CTkLabel(form_inner, text="Mã lớp", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(6, 0))
        self._ma_lop = ctk.CTkEntry(form_inner, placeholder_text="Tự động sinh", state="disabled", height=40)
        self._ma_lop.pack(fill="x", padx=16, pady=(2, 0))
        self._ten_lop = self._field(form_inner, "Tên lớp")
        self._khoi = self._combo(form_inner, "Khối", ["Chọn khối", "Khối 10", "Khối 11", "Khối 12"])

        self._save_btn = build_form_actions(
            form_card,
            self._save,
            self._reset,
            self._delete,
            save_text="Lưu lớp học",
            reset_text="Làm mới form",
            delete_text="Xóa lớp đã chọn",
        )

        list_card = card(body)
        list_card.grid(row=0, column=1, sticky="nsew")

        toolbar = ctk.CTkFrame(list_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=10)
        self._search = ctk.CTkEntry(toolbar, placeholder_text="Tìm theo mã lớp hoặc tên lớp...", height=38)
        self._search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._search.bind("<KeyRelease>", lambda _e: self._on_filter_change())
        self._filter_khoi = ctk.CTkComboBox(
            toolbar,
            values=["Tất cả khối", "Khối 10", "Khối 11", "Khối 12"],
            width=150,
            height=38,
            command=lambda _v: self._on_filter_change(),
        )
        self._filter_khoi.pack(side="left", padx=(0, 8))
        self._filter_khoi.set("Tất cả khối")
        ctk.CTkButton(
            toolbar,
            text="+ Thêm lớp",
            height=38,
            corner_radius=10,
            command=self._on_new_clicked,
            **primary_button_kwargs(),
        ).pack(side="left")

        self._table = DataTable(
            list_card,
            columns=[
                ("ma_lop", "Mã lớp", 85),
                ("ten_lop", "Tên lớp", 160),
                ("khoi", "Khối", 90),
                ("count", "Số HS", 90),
                ("status", "Trạng thái", 135),
            ],
            on_select=self._on_row_select,
        )
        self._table.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._empty_label = ctk.CTkLabel(
            list_card,
            text="Không tìm thấy lớp học phù hợp. Hãy thử đổi từ khóa hoặc bộ lọc khối.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )

        self._pagination = PaginationBar(list_card, on_change=self._render_page, page_size=8)
        self._pagination.pack(fill="x", padx=10, pady=(0, 10))

        if self._on_navigate:
            ScreenNavBar(self, "classes", self._on_navigate).pack(fill="x", pady=(4, 0))

        self._fill_next_id()

    def _field(self, parent, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=label, height=40)
        entry.pack(fill="x", padx=16, pady=(2, 0))
        return entry

    def _combo(self, parent, label: str, values: list) -> ctk.CTkComboBox:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(6, 0))
        combo = ctk.CTkComboBox(parent, values=values, height=40)
        if values:
            combo.set(values[0])
        combo.pack(fill="x", padx=16, pady=(2, 0))
        return combo

    def _on_filter_change(self) -> None:
        self._pagination.reset()
        self.refresh()

    def _set_ma_lop(self, ma_lop: str) -> None:
        self._ma_lop.configure(state="normal")
        self._ma_lop.delete(0, "end")
        self._ma_lop.insert(0, ma_lop)
        self._ma_lop.configure(state="disabled")

    def _get_ma_lop(self) -> str:
        self._ma_lop.configure(state="normal")
        ma_lop = self._ma_lop.get().strip()
        self._ma_lop.configure(state="disabled")
        return ma_lop

    def _fill_next_id(self) -> None:
        self._set_ma_lop(school_class_service.generate_next_id())

    def _clear_other_fields(self) -> None:
        self._ten_lop.delete(0, "end")
        self._khoi.set("Chọn khối")

    def _khoi_to_value(self, text: str) -> str | None:
        if text in ("Chọn khối", "Chá»n khá»‘i"):
            return None
        if text.startswith("Khối "):
            return text.replace("Khối ", "").strip()
        if text.startswith("Khá»‘i "):
            return text.replace("Khá»‘i ", "").strip()
        return text.strip() or None

    def _value_to_khoi_label(self, value: str | None) -> str:
        return f"Khối {value}" if value else "Chọn khối"

    def _format_khoi_badge(self, value: str | None) -> str:
        return f"[Khối {value}]" if value else "[Chưa chọn]"

    def _format_status(self, count: int) -> str:
        return "Đang hoạt động" if count > 0 else "Chưa có HS"

    def _form_to_model(self) -> LopInfo:
        return LopInfo(ma_lop=self._get_ma_lop(), ten_lop=self._ten_lop.get().strip(), khoi=self._khoi_to_value(self._khoi.get()))

    def _fill_form(self, lop: LopInfo) -> None:
        self._editing_id = lop.ma_lop
        self._pending_new = False
        self._set_ma_lop(lop.ma_lop)
        self._ten_lop.delete(0, "end")
        self._ten_lop.insert(0, lop.ten_lop)
        self._khoi.set(self._value_to_khoi_label(lop.khoi))
        self._save_btn.configure(text="Cập nhật lớp học")

    def _reset(self) -> None:
        self._editing_id = None
        self._pending_new = False
        self._fill_next_id()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu lớp học")

    def _on_new_clicked(self) -> None:
        if self._pending_new:
            messagebox.showwarning(
                "Đang thêm mới",
                "Ban đang thêm mới lớp học. Vui lòng lưu hoặc chọn một lớp khác trước khi thêm mới tiếp.",
            )
            return

        self._editing_id = None
        self._pending_new = True
        self._fill_next_id()
        self._clear_other_fields()
        self._save_btn.configure(text="Lưu lớp học")

    def _on_row_select(self, values: tuple) -> None:
        lop = school_class_service.get_class(values[0])
        if lop:
            self._fill_form(lop)

    def _on_table_action(self, action: str, values: tuple) -> None:
        if not values:
            return
        ma_lop = values[0]
        if action == "edit":
            lop = school_class_service.get_class(ma_lop)
            if lop:
                self._fill_form(lop)
            return
        if action == "delete":
            self._editing_id = ma_lop
            self._delete()
            return
        if action == "view":
            if self._on_navigate:
                self._on_navigate("students")
            else:
                messagebox.showinfo("Xem học sinh", f"Chọn bộ lọc lớp {ma_lop} trong màn Học sinh.")

    def _save(self) -> None:
        try:
            lop = self._form_to_model()
            if self._editing_id:
                lop.ma_lop = self._editing_id
                school_class_service.update_class(lop)
                messagebox.showinfo("Thành công", "Đã cập nhật lớp.")
            else:
                school_class_service.create_class(lop)
                messagebox.showinfo("Thành công", "Đã thêm lớp mới.")
            self._notify()
            self._reset()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete(self) -> None:
        ma_lop = self._editing_id or self._get_ma_lop()
        if not ma_lop:
            messagebox.showwarning("Cảnh báo", "Chọn lớp cần xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Xóa lớp {ma_lop}?"):
            return
        try:
            school_class_service.delete_class(ma_lop)
            messagebox.showinfo("Thành công", "Đã xóa lớp.")
            self._notify()
            self._reset()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def _notify(self) -> None:
        if self._on_data_changed:
            self._on_data_changed()

    def _update_kpis(self, classes: list) -> None:
        class_counts = [(c, school_class_service.student_count(c.ma_lop)) for c in classes]
        total_students = sum(count for _c, count in class_counts)
        empty_classes = len([1 for _c, count in class_counts if count == 0])
        largest = max(class_counts, key=lambda item: item[1], default=(None, 0))
        largest_label = largest[0].ten_lop if largest[0] else "—"
        self._class_kpis["classes"].set_value(str(len(classes)))
        self._class_kpis["students"].set_value(str(total_students))
        self._class_kpis["empty"].set_value(str(empty_classes))
        self._class_kpis["largest"].set_value(largest_label, subtitle=f"{largest[1]} học sinh")

    def _render_page(self) -> None:
        page_rows = self._pagination.slice(self._all_rows)
        self._table.load(page_rows)
        if page_rows:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(fill="x", padx=16, pady=(2, 10))

    def refresh(self) -> None:
        search = self._search.get().strip().lower()
        classes = school_class_service.list_classes()
        self._update_kpis(classes)
        if search:
            classes = [c for c in classes if search in c.ma_lop.lower() or search in c.ten_lop.lower()]
        filter_khoi = self._filter_khoi.get()
        if filter_khoi != "Tất cả khối":
            khoi_value = self._khoi_to_value(filter_khoi)
            classes = [c for c in classes if c.khoi == khoi_value]
        self._all_rows = []
        for c in classes:
            count = school_class_service.student_count(c.ma_lop)
            self._all_rows.append((
                c.ma_lop,
                c.ten_lop,
                self._format_khoi_badge(c.khoi),
                f"{count} học sinh",
                self._format_status(count),
            ))
        self._render_page()
