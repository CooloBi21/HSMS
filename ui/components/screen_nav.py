from typing import Callable, Optional

import customtkinter as ctk

from ui.theme import outline_button_kwargs

NAV_ORDER = ["dashboard", "admissions", "students", "accounts", "profiles", "training", "exams", "finance", "affairs", "graduation", "classes", "teachers"]
NAV_LABELS = {
    "dashboard": "Tổng quan",
    "admissions": "Tuyển sinh",
    "students": "Học sinh",
    "accounts": "Tài khoản",
    "profiles": "Hồ sơ",
    "training": "Đào tạo",
    "exams": "Khảo thí",
    "finance": "Tài chính",
    "affairs": "Công tác SV",
    "graduation": "Tốt nghiệp",
    "classes": "Lớp học",
    "teachers": "Giáo viên",
}


class ScreenNavBar(ctk.CTkFrame):
    def __init__(self, master, current: str, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._current = current
        self._on_navigate = on_navigate

        idx = NAV_ORDER.index(current) if current in NAV_ORDER else 0
        prev_key: Optional[str] = NAV_ORDER[idx - 1] if idx > 0 else None
        next_key: Optional[str] = NAV_ORDER[idx + 1] if idx < len(NAV_ORDER) - 1 else None

        if prev_key:
            ctk.CTkButton(
                self,
                text=f"← {NAV_LABELS[prev_key]}",
                height=34,
                corner_radius=10,
                command=lambda: on_navigate(prev_key),
                **outline_button_kwargs(),
            ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            self,
            text=f"Đang xem: {NAV_LABELS.get(current, current)}",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray65"),
        ).pack(side="left", expand=True)

        if next_key:
            ctk.CTkButton(
                self,
                text=f"{NAV_LABELS[next_key]} →",
                height=34,
                corner_radius=10,
                command=lambda: on_navigate(next_key),
                **outline_button_kwargs(),
            ).pack(side="right", padx=(8, 0))
