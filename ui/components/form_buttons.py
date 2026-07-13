import customtkinter as ctk
from typing import Callable

from ui.theme import danger_button_kwargs, outline_button_kwargs, primary_button_kwargs


def build_form_actions(
    parent,
    on_save: Callable,
    on_reset: Callable,
    on_delete: Callable,
    save_text: str = "Lưu",
    reset_text: str = "Thêm mới",
    delete_text: str = "Xóa",
) -> ctk.CTkButton:
    wrapper = ctk.CTkFrame(parent, fg_color="transparent")
    wrapper.pack(fill="x", padx=12, pady=12)
    wrapper.grid_columnconfigure(0, weight=1)

    save_btn = ctk.CTkButton(wrapper, text=save_text, height=38, corner_radius=10, command=on_save, **primary_button_kwargs())
    save_btn.grid(row=0, column=0, sticky="ew", pady=(0, 6))

    ctk.CTkButton(
        wrapper, text=reset_text, height=38, corner_radius=10, command=on_reset, **outline_button_kwargs()
    ).grid(row=1, column=0, sticky="ew", pady=(0, 6))

    ctk.CTkButton(
        wrapper, text=delete_text, height=38, corner_radius=10, command=on_delete, **danger_button_kwargs()
    ).grid(row=2, column=0, sticky="ew")

    return save_btn
