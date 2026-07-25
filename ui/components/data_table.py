import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, List, Optional

import customtkinter as ctk

from ui.theme import BORDER_LIGHT, PRIMARY, TEXT_MAIN, TEXT_MUTED


class DataTable(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns: List[tuple],
        on_select: Optional[Callable] = None,
        on_action: Optional[Callable[[str, tuple], None]] = None,
        action_column: str = "actions",
        action_names: Optional[tuple] = None,
        **kwargs,
    ):
        super().__init__(master, corner_radius=14, border_width=1, border_color=BORDER_LIGHT, **kwargs)
        self._action_column = action_column
        self._action_column_indices = [index for index, column in enumerate(columns) if column[0] == action_column]
        self._columns = [column for column in columns if column[0] != action_column]
        self._on_select = on_select
        self._on_action = on_action
        self._action_names = action_names or ("edit", "delete")
        self._tree: Optional[ttk.Treeview] = None
        self._build()

    def _build(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        self._style = style
        self._apply_style()

        fg = self.cget("fg_color")
        bg = fg[1] if isinstance(fg, (tuple, list)) and len(fg) > 1 else (fg if isinstance(fg, str) else "#2b2b2b")
        container = tk.Frame(self, bg=bg)
        container.pack(fill="both", expand=True, padx=4, pady=4)

        col_ids = [c[0] for c in self._columns]
        self._tree = ttk.Treeview(
            container,
            columns=col_ids,
            show="headings",
            style="HSMS.Treeview",
            selectmode="browse",
        )
        for col_id, heading, width in self._columns:
            self._tree.heading(col_id, text=heading)
            self._tree.column(col_id, width=width, anchor="w")

        vsb = ttk.Scrollbar(container, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        if self._on_select:
            self._tree.bind("<<TreeviewSelect>>", self._handle_select)
        if self._on_action:
            self._tree.bind("<ButtonRelease-1>", self._handle_click)

    def _apply_style(self) -> None:
        dark = ctk.get_appearance_mode().lower() == "dark"
        bg = "#1e293b" if dark else "#ffffff"
        alt = "#0f172a" if dark else "#f8fafc"
        fg = "#f8fafc" if dark else "#111827"
        muted = "#94a3b8" if dark else "#374151"
        self._style.configure(
            "HSMS.Treeview",
            rowheight=32,
            font=("Segoe UI", 11),
            borderwidth=0,
            background=bg,
            fieldbackground=bg,
            foreground=fg,
        )
        self._style.configure(
            "HSMS.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=alt,
            foreground=muted,
            relief="flat",
            borderwidth=0,
        )
        self._style.map(
            "HSMS.Treeview",
            background=[("selected", "#dbeafe" if not dark else "#1e40af")],
            foreground=[("selected", "#111827" if not dark else "#ffffff")],
        )

    def _handle_select(self, _event=None) -> None:
        if not self._tree or not self._on_select:
            return
        sel = self._tree.selection()
        if sel:
            self._on_select(self._tree.item(sel[0], "values"))

    def _handle_click(self, event) -> None:
        if not self._tree or not self._on_action:
            return
        row_id = self._tree.identify_row(event.y)
        column = self._tree.identify_column(event.x)
        if not row_id or not column:
            return
        col_index = int(column.replace("#", "")) - 1
        if col_index < 0 or col_index >= len(self._columns):
            return
        if self._columns[col_index][0] != self._action_column:
            return
        bbox = self._tree.bbox(row_id, column)
        if not bbox:
            return
        relative_x = event.x - bbox[0]
        action_index = min(len(self._action_names) - 1, int(relative_x / max(1, bbox[2]) * len(self._action_names)))
        action = self._action_names[action_index]
        self._on_action(action, self._tree.item(row_id, "values"))

    def clear(self) -> None:
        if self._tree:
            for item in self._tree.get_children():
                self._tree.delete(item)

    def load(self, rows: Iterable[tuple]) -> None:
        self.clear()
        if self._tree:
            self._apply_style()
            dark = ctk.get_appearance_mode().lower() == "dark"
            for index, row in enumerate(rows):
                tags = ("even",) if index % 2 == 0 else ("odd",)
                values = tuple(value for value_index, value in enumerate(row) if value_index not in self._action_column_indices)
                self._tree.insert("", "end", values=values, tags=tags)
            self._tree.tag_configure("even", background="#1e293b" if dark else "#ffffff")
            self._tree.tag_configure("odd", background="#0f172a" if dark else "#f8fafc")

    def get_selected_values(self) -> Optional[tuple]:
        if not self._tree:
            return None
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0], "values")
