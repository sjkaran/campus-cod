"""
Screen 6 — Departmental Analytics.

Charts are drawn with plain tk.Canvas bars rather than pulling in
matplotlib, keeping the prototype dependency-free per the spec
("use an appropriate charting solution... without adding unnecessary
dependencies"). Swap in a real charting lib later if needed — the
data-fetching stays in services/analytics_service.py either way.
"""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts
from services import analytics_service
from ui.widgets import Card, StatCard, SectionHeader


class AnalyticsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        self._build()

    def _build(self):
        header = SectionHeader(self, "Departmental Analytics", "Attendance trends across subjects and semesters")
        header.pack(fill="x")

        dist = analytics_service.get_attendance_distribution()
        avg = analytics_service.get_department_average()

        stat_row = ttk.Frame(self, style="App.TFrame")
        stat_row.pack(fill="x", pady=(16, 16))
        for i in range(4):
            stat_row.columnconfigure(i, weight=1, uniform="stat")

        StatCard(stat_row, "Average Attendance", f"{avg}%", tone="success").grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        StatCard(stat_row, "Total Students", dist["total"], tone="default").grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        StatCard(stat_row, "Below Threshold", dist["attention"], tone="danger").grid(row=0, column=2, sticky="nsew", padx=(0, 10))
        StatCard(stat_row, "On Track (Good)", dist["good"], tone="success").grid(row=0, column=3, sticky="nsew")

        charts = ttk.Frame(self, style="App.TFrame")
        charts.pack(fill="both", expand=True)
        charts.columnconfigure(0, weight=1)
        charts.columnconfigure(1, weight=1)
        charts.rowconfigure(0, weight=1)
        charts.rowconfigure(1, weight=1)

        self._distribution_card(charts, dist).grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        self._subject_wise_card(charts).grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        self._semester_wise_card(charts).grid(row=1, column=0, columnspan=2, sticky="nsew")

    # ------------------------------------------------------------------
    def _distribution_card(self, parent, dist):
        card = Card(parent)
        ttk.Label(card, text="Attendance Distribution", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(card, width=260, height=180, bg=Colors.CARD_BG, highlightthickness=0)
        canvas.pack()

        total = max(dist["total"], 1)
        segments = [
            ("Good", dist["good"], Colors.ATTN_GOOD),
            ("Normal", dist["normal"], Colors.ATTN_NORMAL),
            ("Attention", dist["attention"], Colors.ATTN_LOW),
        ]

        x, y, w, h = 20, 20, 220, 24
        offset = 0
        for label, count, color in segments:
            frac = count / total
            seg_w = w * frac
            if seg_w > 0:
                canvas.create_rectangle(x + offset, y, x + offset + seg_w, y + h, fill=color, outline="")
            offset += seg_w

        legend_y = y + h + 20
        for label, count, color in segments:
            canvas.create_oval(x, legend_y - 5, x + 10, legend_y + 5, fill=color, outline="")
            pct = round((count / total) * 100, 1) if total else 0
            canvas.create_text(x + 18, legend_y, anchor="w", font=Fonts.SMALL,
                                text=f"{label}: {count} students ({pct}%)")
            legend_y += 22

        return card

    def _subject_wise_card(self, parent):
        card = Card(parent)
        ttk.Label(card, text="Subject-wise Attendance", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))
        data = analytics_service.get_subject_wise_attendance()
        self._bar_chart(card, [(d["subject"], d["percentage"]) for d in data], width=260, height=180)
        return card

    def _semester_wise_card(self, parent):
        card = Card(parent)
        ttk.Label(card, text="Semester-wise Attendance", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))
        data = analytics_service.get_semester_wise_attendance()
        self._bar_chart(
            card, [(f"Sem {d['semester']}", d["percentage"]) for d in data],
            width=560, height=140, horizontal_labels=True,
        )
        return card

    def _bar_chart(self, parent, data, width=260, height=180, horizontal_labels=False):
        canvas = tk.Canvas(parent, width=width, height=height, bg=Colors.CARD_BG, highlightthickness=0)
        canvas.pack(fill="x")

        if not data:
            canvas.create_text(width // 2, height // 2, text="No data", fill=Colors.TEXT_MUTED, font=Fonts.SMALL)
            return

        padding_left = 34
        padding_bottom = 34
        chart_h = height - padding_bottom - 10
        chart_w = width - padding_left - 10
        n = len(data)
        bar_w = chart_w / n * 0.55
        gap = chart_w / n

        # y-axis gridlines at 0/50/100
        for pct in (0, 50, 100):
            y = 10 + chart_h - (chart_h * pct / 100)
            canvas.create_line(padding_left, y, width - 5, y, fill=Colors.BORDER)
            canvas.create_text(padding_left - 6, y, text=str(pct), anchor="e", font=Fonts.SMALL, fill=Colors.TEXT_MUTED)

        for i, (label, pct) in enumerate(data):
            bar_h = chart_h * min(pct, 100) / 100
            x0 = padding_left + i * gap + (gap - bar_w) / 2
            y0 = 10 + chart_h - bar_h
            x1 = x0 + bar_w
            y1 = 10 + chart_h
            color = Colors.ATTN_GOOD if pct >= 90 else Colors.ATTN_NORMAL if pct >= 75 else Colors.ATTN_LOW
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            canvas.create_text((x0 + x1) / 2, y0 - 8, text=f"{pct}%", font=Fonts.SMALL_BOLD, fill=Colors.TEXT_PRIMARY)
            label_text = label if horizontal_labels else _wrap_label(label)
            canvas.create_text((x0 + x1) / 2, height - padding_bottom + 14, text=label_text,
                                font=Fonts.SMALL, fill=Colors.TEXT_SECONDARY, width=gap)


def _wrap_label(text, max_len=10):
    return text if len(text) <= max_len else text[:max_len - 1] + "…"
