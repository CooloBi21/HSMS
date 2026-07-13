import customtkinter as ctk

THEME_KEY = "hsms_theme"

BG_MAIN = ("#f8fafc", "#0f172a")
BG_CARD = ("#ffffff", "#1e293b")
BORDER_LIGHT = ("#e5e7eb", "#334155")
TEXT_MAIN = ("#111827", "#f8fafc")
TEXT_MUTED = ("#6b7280", "#94a3b8")
PRIMARY = "#2563eb"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"

# Màu chữ nút — (sáng, tối)
BTN_TEXT_ON_SOLID = "#ffffff"
BTN_TEXT_OUTLINE = (PRIMARY, "#bfdbfe")
BTN_TEXT_NAV_IDLE = ("#374151", "#e2e8f0")
BTN_TEXT_NAV_ACTIVE = "#ffffff"
BTN_TEXT_DISABLED = ("#64748b", "#94a3b8")
BTN_BORDER_OUTLINE = ("#bfdbfe", "#475569")
BTN_HOVER_OUTLINE = ("#eff6ff", "#334155")
BTN_BG_DISABLED = ("#e2e8f0", "#374151")

BTN_PRIMARY = (PRIMARY, "#1d4ed8")
BTN_PRIMARY_HOVER = ("#1d4ed8", "#1e40af")


def apply_theme(mode: str) -> None:
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")


def toggle_theme(current: str) -> str:
    new_mode = "dark" if current == "light" else "light"
    apply_theme(new_mode)
    return new_mode


def outline_button_kwargs() -> dict:
    """Nút viền / nền trong suốt — chữ đậm trên nền sáng."""
    return dict(
        fg_color="transparent",
        border_width=1,
        border_color=BTN_BORDER_OUTLINE,
        text_color=BTN_TEXT_OUTLINE,
        hover_color=BTN_HOVER_OUTLINE,
    )


def primary_button_kwargs() -> dict:
    return dict(
        fg_color=BTN_PRIMARY,
        hover_color=BTN_PRIMARY_HOVER,
        text_color=BTN_TEXT_ON_SOLID,
        text_color_disabled=BTN_TEXT_DISABLED,
    )


def danger_button_kwargs() -> dict:
    return dict(
        fg_color="#ef4444",
        hover_color="#dc2626",
        text_color=BTN_TEXT_ON_SOLID,
    )


def accent_button_kwargs(color: str) -> dict:
    return dict(
        fg_color=color,
        hover_color=color,
        text_color=BTN_TEXT_ON_SOLID,
    )


def nav_idle_button_kwargs() -> dict:
    return dict(
        fg_color="transparent",
        text_color=BTN_TEXT_NAV_IDLE,
        hover_color=BTN_HOVER_OUTLINE,
    )


def card(parent, **kwargs) -> ctk.CTkFrame:
    defaults = dict(corner_radius=16, border_width=1, fg_color=BG_CARD, border_color=BORDER_LIGHT)
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def heading(parent, text: str, size: int = 22) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size, weight="bold"), text_color=TEXT_MAIN)


def subheading(parent, text: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
