import customtkinter as ctk

from config import APP_SIZE, APP_TITLE, MIN_SIZE
from ui.theme import (
    BG_CARD,
    BORDER_LIGHT,
    apply_theme,
    outline_button_kwargs,
    toggle_theme,
)
from ui.views.business_view import BusinessView
from ui.views.classes_view import ClassesView
from ui.views.dashboard_view import DashboardView
from ui.views.students_view import StudentsView
from ui.views.teachers_view import TeachersView


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
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="HSMS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
        ).grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")
        ctk.CTkLabel(
            sidebar,
            text="Quan ly Hoc sinh",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        nav_items = [
            ("dashboard", "Dashboard"),
            ("students", "Hoc sinh"),
            ("classes", "Lop hoc"),
            ("teachers", "Giao vien"),
            ("business", "Nghiep vu"),
        ]
        for i, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                height=40,
                corner_radius=10,
                fg_color="transparent",
                text_color=("gray20", "gray90"),
                hover_color=("#e8eef8", "#1e3a5f"),
                command=lambda k=key: self._show_view(k),
            )
            btn.grid(row=i, column=0, padx=14, pady=4, sticky="ew")
            self._nav_buttons[key] = btn

        self._theme_btn = ctk.CTkButton(
            sidebar,
            text="Che do toi",
            corner_radius=10,
            command=self._toggle_theme,
            **outline_button_kwargs(),
        )
        self._theme_btn.grid(row=9, column=0, padx=14, pady=(8, 20), sticky="ew")

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
        self._views["students"] = StudentsView(
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
        self._views["business"] = BusinessView(
            self._container,
            on_data_changed=on_change,
            on_navigate=navigate,
        )

    def _on_data_changed(self) -> None:
        self._views["dashboard"].refresh()
        self._views["students"].refresh()
        self._views["classes"].refresh()
        self._views["teachers"].refresh()
        self._views["business"].refresh()

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
        self._theme_btn.configure(text="Che do sang" if self._theme_mode == "dark" else "Che do toi")
        self._views["dashboard"].refresh()
