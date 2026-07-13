import math
from typing import Callable, List, TypeVar

import customtkinter as ctk

from ui.theme import BTN_BG_DISABLED, BTN_TEXT_DISABLED, primary_button_kwargs

T = TypeVar("T")


class PaginationBar(ctk.CTkFrame):
    def __init__(self, master, on_change: Callable[[], None], page_size: int = 8, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._page_size = page_size
        self._page = 1
        self._total = 0

        btn_style = primary_button_kwargs()
        self._prev_btn = ctk.CTkButton(
            self, text="◀ Trang trước", width=120, height=32, command=self._prev, **btn_style
        )
        self._prev_btn.pack(side="left", padx=(0, 6))

        self._info = ctk.CTkLabel(self, text="Trang 1/1", font=ctk.CTkFont(size=12), text_color=("gray20", "gray80"))
        self._info.pack(side="left", padx=6)

        self._next_btn = ctk.CTkButton(
            self, text="Trang sau ▶", width=120, height=32, command=self._next, **btn_style
        )
        self._next_btn.pack(side="left", padx=(6, 0))

        self._count_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11), text_color=("gray45", "gray60")
        )
        self._count_label.pack(side="right")

    @property
    def page(self) -> int:
        return self._page

    def reset(self) -> None:
        self._page = 1

    def set_total(self, total: int) -> None:
        self._total = total
        max_page = max(1, math.ceil(total / self._page_size) if total else 1)
        if self._page > max_page:
            self._page = max_page
        self._update_buttons()

    def slice(self, items: List[T]) -> List[T]:
        self.set_total(len(items))
        start = (self._page - 1) * self._page_size
        return items[start : start + self._page_size]

    def _prev(self) -> None:
        if self._page > 1:
            self._page -= 1
            self._on_change()

    def _next(self) -> None:
        max_page = max(1, math.ceil(self._total / self._page_size) if self._total else 1)
        if self._page < max_page:
            self._page += 1
            self._on_change()

    def _update_buttons(self) -> None:
        max_page = max(1, math.ceil(self._total / self._page_size) if self._total else 1)
        self._info.configure(text=f"Trang {self._page}/{max_page}")
        self._count_label.configure(text=f"Tổng: {self._total} bản ghi")
        self._prev_btn.configure(state="normal" if self._page > 1 else "disabled")
        self._next_btn.configure(state="normal" if self._page < max_page else "disabled")
