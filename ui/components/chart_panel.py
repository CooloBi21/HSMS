from typing import Dict, List

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ui.theme import BG_CARD, BORDER_LIGHT


class ChartPanel(ctk.CTkFrame):
    def __init__(self, master, title: str, chart_type: str = "bar", **kwargs):
        super().__init__(master, corner_radius=16, border_width=1, fg_color=BG_CARD, border_color=BORDER_LIGHT, **kwargs)
        self._chart_type = chart_type
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=14, pady=(12, 4)
        )
        self._fig = Figure(figsize=(4.6, 2.65), dpi=100)
        self._fig.patch.set_alpha(0.0)
        self._ax = self._fig.add_subplot(111)
        plot_host = ctk.CTkFrame(self, fg_color="transparent")
        plot_host.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=plot_host)
        self._mpl_canvas.get_tk_widget().pack(fill="both", expand=True)

    def render(self, data: List[Dict], dark: bool = False) -> None:
        self._ax.clear()
        bg = "#1e293b" if dark else "#ffffff"
        fg = "#f8fafc" if dark else "#111827"
        muted = "#94a3b8" if dark else "#6b7280"
        self._fig.patch.set_facecolor(bg)
        self._ax.set_facecolor(bg)
        self._ax.tick_params(colors=muted, labelsize=8)
        for spine in self._ax.spines.values():
            spine.set_visible(False)

        labels = [d["label"] for d in data]
        values = [d["value"] for d in data]

        if not data:
            self._ax.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center", color=fg)
            self._mpl_canvas.draw()
            return

        colors = ["#2563eb", "#10b981", "#06b6d4", "#f59e0b", "#7c3aed", "#ef4444", "#94a3b8"]

        if self._chart_type == "pie":
            wedges, _texts, autotexts = self._ax.pie(
                values,
                labels=None,
                autopct="%1.0f%%",
                startangle=90,
                pctdistance=0.78,
                colors=colors[: len(values)],
                wedgeprops={"width": 0.42, "edgecolor": bg, "linewidth": 2},
                textprops={"color": fg, "fontsize": 8, "weight": "bold"},
            )
            self._ax.legend(
                wedges,
                labels,
                loc="center left",
                bbox_to_anchor=(0.92, 0.5),
                frameon=False,
                labelcolor=fg,
                fontsize=8,
            )
            for text in autotexts:
                text.set_color("#ffffff")
            self._ax.axis("equal")
        else:
            bars = self._ax.barh(labels, values, color=self._bar_colors(values, colors), edgecolor="none", linewidth=0, height=0.58)
            self._ax.grid(axis="x", color="#e5e7eb" if not dark else "#334155", linewidth=0.8)
            self._ax.set_axisbelow(True)
            self._ax.invert_yaxis()
            plt.setp(self._ax.get_yticklabels(), color=fg)
            plt.setp(self._ax.get_xticklabels(), color=muted)
            max_value = max(values) if values else 0
            self._ax.set_xlim(0, max_value * 1.18 if max_value else 1)
            for bar, val in zip(bars, values):
                self._ax.text(
                    bar.get_width(),
                    bar.get_y() + bar.get_height() / 2,
                    f" {val}",
                    ha="left",
                    va="center",
                    fontsize=9,
                    color=fg,
                )

        self._fig.tight_layout()
        self._mpl_canvas.draw()

    def _bar_colors(self, values: List[float], colors: List[str]) -> List[str]:
        if self._chart_type != "score_bar" or len(values) < 2:
            return [colors[0]] * len(values)
        min_value = min(values)
        max_value = max(values)
        result = []
        for value in values:
            if value == max_value:
                result.append("#10b981")
            elif value == min_value:
                result.append("#f59e0b")
            else:
                result.append("#2563eb")
        return result
