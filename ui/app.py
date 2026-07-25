import customtkinter as ctk

from config import APP_SIZE, APP_TITLE, MIN_SIZE
from ui.theme import (
    BG_CARD,
    BORDER_LIGHT,
    apply_theme,
    outline_button_kwargs,
    toggle_theme,
)
from ui.views.accounts_view import AccountsView
from ui.views.admissions_view import AdmissionsView
from ui.views.classes_view import ClassesView
from ui.views.dashboard_view import DashboardView
from ui.views.exams_view import ExamsView
from ui.views.finance_view import FinanceView
from ui.views.graduation_view import GraduationView
from ui.views.student_affairs_view import StudentAffairsView
from ui.views.student_profiles_view import StudentProfilesView
from ui.views.students_view import StudentsView
from ui.views.teachers_view import TeachersView
from ui.views.training_view import TrainingView


NAV_ITEMS = [
    ("dashboard", "Tổng quan"),
    ("admissions", "Tuyển sinh"),
    ("students", "Học sinh"),
    ("accounts", "Tài khoản"),
    ("profiles", "Hồ sơ"),
    ("training", "Đào tạo"),
    ("exams", "Khảo thí"),
    ("finance", "Tài chính"),
    ("affairs", "Công tác SV"),
    ("graduation", "Tốt nghiệp"),
    ("classes", "Lớp học"),
    ("teachers", "Giáo viên"),
]


class HSMSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._theme_mode = "light"
        apply_theme(self._theme_mode)

        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(*MIN_SIZE)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._views: dict = {}
        self._nav_buttons: dict = {}
        self._build_sidebar()
        self._build_content()
        self._show_view("dashboard")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_LIGHT,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(2, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="HSMS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
        ).grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")
        ctk.CTkLabel(
            sidebar,
            text="Quản lý học sinh",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        nav_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", scrollbar_button_color=("#cbd5e1", "#475569"))
        nav_frame.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="nsew")
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (key, label) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                anchor="w",
                height=42,
                width=180,
                corner_radius=10,
                fg_color="transparent",
                text_color=("gray20", "gray90"),
                hover_color=("#e8eef8", "#1e3a5f"),
                command=lambda k=key: self._show_view(k),
            )
            btn.grid(row=i, column=0, padx=4, pady=4, sticky="ew")
            self._nav_buttons[key] = btn

        self._theme_btn = ctk.CTkButton(
            sidebar,
            text="Chế độ tối",
            height=40,
            corner_radius=10,
            command=self._toggle_theme,
            **outline_button_kwargs(),
        )
        self._theme_btn.grid(row=3, column=0, padx=14, pady=(8, 20), sticky="ew")

    def _build_content(self) -> None:
        self._container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._container.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        on_change = self._on_data_changed
        navigate = lambda key: self._show_view(key)
        self._views["dashboard"] = DashboardView(
            self._container,
            get_theme_mode=lambda: self._theme_mode,
            on_navigate=navigate,
        )
        self._views["admissions"] = AdmissionsView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["students"] = StudentsView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["accounts"] = AccountsView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["profiles"] = StudentProfilesView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["training"] = TrainingView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["exams"] = ExamsView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["finance"] = FinanceView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["affairs"] = StudentAffairsView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["graduation"] = GraduationView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["classes"] = ClassesView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
        self._views["teachers"] = TeachersView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )
    def _on_data_changed(self) -> None:
        self._views["dashboard"].refresh()
        self._views["admissions"].refresh()
        self._views["students"].refresh()
        self._views["accounts"].refresh()
        self._views["profiles"].refresh()
        self._views["training"].refresh()
        self._views["exams"].refresh()
        self._views["finance"].refresh()
        self._views["affairs"].refresh()
        self._views["graduation"].refresh()
        self._views["classes"].refresh()
        self._views["teachers"].refresh()

    def _show_view(self, key: str) -> None:
        for name, view in self._views.items():
            if name == key:
                view.grid(row=0, column=0, sticky="nsew")
                if hasattr(view, "refresh"):
                    view.refresh()
            else:
                view.grid_forget()

        for name, btn in self._nav_buttons.items():
            if name == key:
                btn.configure(fg_color=("#2563eb", "#1d4ed8"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "gray90"))

    def _toggle_theme(self) -> None:
        self._theme_mode = toggle_theme(self._theme_mode)
        self._theme_btn.configure(text="Chế độ sáng" if self._theme_mode == "dark" else "Chế độ tối")
        self._views["dashboard"].refresh()
