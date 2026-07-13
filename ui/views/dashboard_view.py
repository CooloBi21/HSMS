import customtkinter as ctk
from tkinter import messagebox

from services import ai_assistant_service, dashboard_service
from ui.components.chart_panel import ChartPanel
from ui.components.metric_card import MetricCard
from ui.components.pagination import PaginationBar
from ui.components.screen_nav import ScreenNavBar
from ui.theme import (
    DANGER,
    PRIMARY,
    SUCCESS,
    TEXT_MUTED,
    WARNING,
    card,
    heading,
    outline_button_kwargs,
    primary_button_kwargs,
    subheading,
)


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, get_theme_mode, on_navigate=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._get_theme_mode = get_theme_mode
        self._on_navigate = on_navigate
        self._metrics: dict = {}
        self._charts: dict = {}
        self._activity_page = None
        self._build()

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=(0, 16))
        heading(header, "Dashboard điều hành").pack(anchor="w")
        subheading(header, "Tổng quan hệ thống · Cảnh báo · Hành động nhanh").pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Theo doi nhanh tinh hinh hoc sinh, lop hoc, giao vien va hieu suat hoc tap.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(6, 0))

        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 10))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)

        specs = [
            ("students", "Học sinh", "#2563eb", "Tổng số học sinh"),
            ("classes", "Lớp học", "#7c3aed", "Tổng số lớp"),
            ("teachers", "Giáo viên", "#06b6d4", "Tổng số giáo viên"),
            ("avg_score", "Điểm TB toàn trường", "#f59e0b", "Trung bình cộng"),
        ]
        for i, (key, title, color, sub) in enumerate(specs):
            m = MetricCard(kpi_row, title, "0", accent=color, subtitle=sub)
            m.grid(row=0, column=i, padx=5, sticky="nsew")
            self._metrics[key] = m

        actions_row = card(self)
        actions_row.pack(fill="x", pady=(0, 10))
        actions_inner = ctk.CTkFrame(actions_row, fg_color="transparent")
        actions_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(actions_inner, text="Hành động nhanh", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 8)
        )
        btn_row = ctk.CTkFrame(actions_inner, fg_color="transparent")
        btn_row.pack(fill="x")
        for text, target, color, hover_color in [
            ("+ Thêm học sinh", "students", "#2563eb", "#1d4ed8"),
            ("+ Thêm giáo viên", "teachers", "#06b6d4", "#0891b2"),
            ("+ Thêm lớp học", "classes", "#7c3aed", "#6d28d9"),
            ("📊 Nhập điểm", "students", "#10b981", "#059669"),
            ("📋 Xuất báo cáo", None, "#64748b", "#4b5563"),
        ]:
            ctk.CTkButton(
                btn_row, text=text, height=36, corner_radius=10,
                fg_color=color, hover_color=hover_color, text_color="#ffffff",
                command=lambda t=target, lbl=text: self._quick_action(t, lbl),
            ).pack(side="left", padx=(0, 8))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)

        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure((0, 1), weight=1)
        self._charts["students_class"] = ChartPanel(left, "Số học sinh theo lớp", "bar")
        self._charts["students_class"].grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self._charts["score_class"] = ChartPanel(left, "Điểm TB theo lớp", "score_bar")
        self._charts["score_class"].grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self._charts["academic"] = ChartPanel(left, "Phân loại học lực học sinh", "pie")
        self._charts["academic"].grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")

        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        notif_card = card(right)
        notif_card.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(notif_card, text="🔔 Cảnh báo & Thông báo", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 6)
        )
        self._notif_frame = ctk.CTkFrame(notif_card, fg_color="transparent")
        self._notif_frame.pack(fill="x", padx=12, pady=(0, 12))

        act_card = card(right)
        act_card.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(act_card, text="🕐 Hoạt động gần đây", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 6)
        )
        self._activity_frame = ctk.CTkFrame(act_card, fg_color="transparent")
        self._activity_frame.pack(fill="x", padx=12, pady=(0, 4))
        self._activity_page = PaginationBar(act_card, on_change=self._reload_activities, page_size=5)
        self._activity_page.pack(fill="x", padx=12, pady=(0, 12))

        ai_card = card(right)
        ai_card.pack(fill="x")
        ctk.CTkLabel(ai_card, text="🤖 Trợ lý thông minh", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        ctk.CTkLabel(
            ai_card, text="Hỏi nhanh về dữ liệu trường học (tiếng Việt)",
            font=ctk.CTkFont(size=11), text_color=("gray45", "gray60"),
        ).pack(anchor="w", padx=16)
        self._ai_input = ctk.CTkEntry(ai_card, placeholder_text='VD: "Giáo viên nào đang tạm nghỉ?"')
        self._ai_input.pack(fill="x", padx=16, pady=8)
        self._ai_input.bind("<Return>", lambda _e: self._ask_ai())
        ctk.CTkButton(
            ai_card, text="Hỏi ngay", height=34, corner_radius=8, command=self._ask_ai,
            **primary_button_kwargs(),
        ).pack(anchor="w", padx=16, pady=(0, 12))

        if self._on_navigate:
            ScreenNavBar(self, "dashboard", self._on_navigate).pack(fill="x", pady=(12, 4))

    def _reload_activities(self) -> None:
        stats = dashboard_service.get_dashboard_stats(
            activity_page=self._activity_page.page, activity_page_size=5
        )
        self._activity_page.set_total(stats.activity_total)
        self._render_activities(stats.recent_activities)

    def _quick_action(self, target: str | None, label: str) -> None:
        if target and self._on_navigate:
            self._on_navigate(target)
            return
        messagebox.showinfo("Sắp có", f'Tính năng "{label}" sẽ được bổ sung trong phiên bản tiếp theo.')

    def _ask_ai(self) -> None:
        answer = ai_assistant_service.answer_question(self._ai_input.get())
        messagebox.showinfo("Trợ lý thông minh", answer)

    def _render_notifications(self, items: list) -> None:
        for w in self._notif_frame.winfo_children():
            w.destroy()
        styles = {
            "critical": ("Nghiem trong", DANGER, "#fee2e2"),
            "warning": ("Can kiem tra", WARNING, "#fef3c7"),
            "info": ("Thong tin", PRIMARY, "#dbeafe"),
            "success": ("On dinh", SUCCESS, "#d1fae5"),
        }
        for item in items:
            if isinstance(item, dict):
                level = item.get("level", "info")
                title = item.get("title", "Thong tin")
                detail = item.get("detail", "")
            else:
                level = "info"
                title = "Thong tin"
                detail = str(item)
            label, color, soft = styles.get(level, styles["info"])
            row = ctk.CTkFrame(self._notif_frame, fg_color=(soft, "#172554"), corner_radius=12)
            row.pack(fill="x", pady=4)
            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(8, 2))
            ctk.CTkLabel(
                top,
                text=label,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=color,
                fg_color=("#ffffff", "#0f172a"),
                corner_radius=10,
                padx=8,
                pady=2,
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_MUTED,
                wraplength=300,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=10, pady=(2, 0))
            ctk.CTkLabel(
                row,
                text=detail,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED,
                wraplength=300,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=10, pady=(2, 8))

    def _render_activities(self, activities) -> None:
        for w in self._activity_frame.winfo_children():
            w.destroy()
        if not activities:
            ctk.CTkLabel(
                self._activity_frame,
                text="Chưa có hoạt động. Thao tác thêm/sửa/xóa sẽ hiển thị tại đây.",
                text_color=("gray45", "gray60"), wraplength=300, justify="left",
            ).pack(anchor="w")
            return
        for act in activities:
            row = ctk.CTkFrame(self._activity_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            marker = ctk.CTkFrame(row, width=10, height=10, corner_radius=8, fg_color=PRIMARY)
            marker.pack(side="left", anchor="n", pady=5)
            marker.pack_propagate(False)
            detail = ctk.CTkFrame(row, fg_color="transparent")
            detail.pack(side="left", fill="x", expand=True, padx=(10, 0))
            ctk.CTkLabel(
                detail,
                text=act.time_display,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=TEXT_MUTED,
                anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(detail, text=act.action, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(1, 0))
            ctk.CTkLabel(
                detail, text=act.detail, font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED, anchor="w", wraplength=240, justify="left",
            ).pack(fill="x")

    def refresh(self) -> None:
        stats = dashboard_service.get_dashboard_stats(
            activity_page=self._activity_page.page, activity_page_size=5
        )
        self._metrics["students"].set_value(str(stats.student_count))
        self._metrics["classes"].set_value(str(stats.class_count))
        self._metrics["teachers"].set_value(str(stats.teacher_count))
        self._metrics["avg_score"].set_value(
            str(stats.average_score),
            subtitle=f"Tốt nhất: {stats.best_class} · Cần theo dõi: {stats.worst_class}",
        )
        dark = self._get_theme_mode() == "dark"
        self._charts["students_class"].render(stats.students_per_class, dark=dark)
        self._charts["score_class"].render(stats.score_per_class, dark=dark)
        self._charts["academic"].render(stats.academic_distribution, dark=dark)
        self._render_notifications(stats.notifications)
        self._activity_page.set_total(stats.activity_total)
        self._render_activities(stats.recent_activities)
