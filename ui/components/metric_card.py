import customtkinter as ctk

from ui.theme import BG_CARD, BORDER_LIGHT, TEXT_MAIN, TEXT_MUTED


class MetricCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        accent: str = "#2563eb",
        subtitle: str = "",
        icon: str = "•",
        badge: str = "",
        **kwargs,
    ):
        super().__init__(master, corner_radius=16, border_width=1, fg_color=BG_CARD, border_color=BORDER_LIGHT, **kwargs)
        self._accent = accent

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))

        icon_box = ctk.CTkFrame(top, width=38, height=38, corner_radius=12, fg_color=(self._soft_color(accent), "#1e3a5f"))
        icon_box.pack(side="left", anchor="n")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=ctk.CTkFont(size=17, weight="bold"), text_color=accent).pack(expand=True)

        title_box = ctk.CTkFrame(top, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True, padx=(12, 0))
        ctk.CTkLabel(
            title_box, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_MAIN
        ).pack(anchor="w")
        if badge:
            ctk.CTkLabel(
                title_box,
                text=badge,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=accent,
                fg_color=(self._soft_color(accent), "#172554"),
                corner_radius=12,
                padx=8,
                pady=2,
            ).pack(anchor="w", pady=(5, 0))

        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=34, weight="bold"), text_color=TEXT_MAIN
        )
        self.value_label.pack(anchor="w", padx=18, pady=(14, 0))

        self._subtitle_label = ctk.CTkLabel(
            self, text=subtitle, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED, anchor="w", justify="left"
        )
        self._subtitle_label.pack(anchor="w", fill="x", padx=18, pady=(2, 16))

    def _soft_color(self, accent: str) -> str:
        soft = {
            "#2563eb": "#dbeafe",
            "#10b981": "#d1fae5",
            "#06b6d4": "#cffafe",
            "#f59e0b": "#fef3c7",
            "#7c3aed": "#ede9fe",
            "#ef4444": "#fee2e2",
        }
        return soft.get(accent, "#e5e7eb")

    def set_value(self, value: str, subtitle: str = "") -> None:
        self.value_label.configure(text=value)
        if subtitle:
            self._subtitle_label.configure(text=subtitle)
