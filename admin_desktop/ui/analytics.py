"""Analytics Dashboard — institution-level insight using bar/donut visualizations."""

import tkinter as tk

from config.settings import COLORS, FONTS, PADDING
from services import analytics_service
from ui.components import Card, KPICard, BarChart, DonutChart, LegendList
from utils.formatters import format_number, format_percentage


class AnalyticsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        data = analytics_service.get_analytics()

        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Analytics", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(0, PADDING["lg"]))

        # Top KPI strip -------------------------------------------------
        kpi_row = tk.Frame(content, bg=COLORS["bg"])
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="k")
        KPICard(kpi_row, "Total Students", format_number(data.total_students), "primary").grid(
            row=0, column=0, sticky="nsew", padx=(0, 8))
        KPICard(kpi_row, "Overall Attendance", format_percentage(data.overall_attendance), "success").grid(
            row=0, column=1, sticky="nsew", padx=8)
        KPICard(kpi_row, "Low-Attendance Students", format_number(data.low_attendance_students), "warning").grid(
            row=0, column=2, sticky="nsew", padx=8)
        KPICard(kpi_row, "Pending Gate Passes", format_number(data.gatepass_pending), "danger").grid(
            row=0, column=3, sticky="nsew", padx=(8, 0))

        # Two-column grid of analytical cards -----------------------------
        grid = tk.Frame(content, bg=COLORS["bg"])
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1, uniform="g")
        grid.grid_columnconfigure(1, weight=1, uniform="g")

        # Students by department (answers: "where are our students concentrated?")
        c1 = Card(grid, title="Students by Department")
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        BarChart(c1.body, data.students_by_department, width=420, height=220).pack()

        # Attendance by department (answers: "which department needs attention?")
        c2 = Card(grid, title="Attendance by Department")
        c2.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        BarChart(c2.body, data.attendance_by_department, width=420, height=220,
                  max_value=100, value_fmt=lambda v: f"{v}%").pack()

        # Attendance by subject (answers: "which subjects have low attendance?")
        c3 = Card(grid, title="Attendance by Subject")
        c3.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        BarChart(c3.body, data.attendance_by_subject, width=420, height=220,
                  max_value=100, value_fmt=lambda v: f"{v}%").pack()

        # Students by semester
        c4 = Card(grid, title="Students by Semester")
        c4.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        sem_data = {f"S{k}": v for k, v in sorted(data.students_by_semester.items())}
        BarChart(c4.body, sem_data, width=420, height=220).pack()

        # Gate-pass breakdown (donut + legend)
        c5 = Card(grid, title="Gate-Pass Status Breakdown")
        c5.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        gp_wrap = tk.Frame(c5.body, bg=COLORS["surface"])
        gp_wrap.pack()
        gp_data = {"Pending": data.gatepass_pending, "Approved": data.gatepass_approved,
                    "Rejected": data.gatepass_rejected}
        DonutChart(gp_wrap, gp_data, width=180, height=180).pack(side="left")
        LegendList(gp_wrap, gp_data).pack(side="left", padx=(16, 0), fill="y")

        # Notifications by audience (donut + legend)
        c6 = Card(grid, title="Notifications by Audience")
        c6.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        notif_wrap = tk.Frame(c6.body, bg=COLORS["surface"])
        notif_wrap.pack()
        notif_data = {k.replace("_", " ").title(): v for k, v in data.notifications_by_audience.items()}
        DonutChart(notif_wrap, notif_data, width=180, height=180).pack(side="left")
        LegendList(notif_wrap, notif_data).pack(side="left", padx=(16, 0), fill="y")
