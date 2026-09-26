"""Attendance Management — institution-wide monitoring (view only, no edits)."""

import tkinter as tk

from config.settings import COLORS, FONTS, PADDING
from services import attendance_service, student_service
from ui.components import DataTable, FilterBar, StatePlaceholder, Card, status_badge
from utils.formatters import format_percentage


def _attendance_status(pct: float) -> str:
    if pct < 65.0:
        return "CRITICAL"
    if pct < 75.0:
        return "BELOW THRESHOLD"
    return "HEALTHY"


class AttendanceScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Attendance", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        # Summary strip
        summary = attendance_service.get_attendance_summary()
        summary_row = tk.Frame(self, bg=COLORS["bg"])
        summary_row.pack(fill="x", padx=PADDING["xl"])
        for i in range(3):
            summary_row.grid_columnconfigure(i, weight=1, uniform="s")
        self._summary_card(summary_row, "Overall Attendance", format_percentage(summary.overall_percentage),
                             "primary").grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        self._summary_card(summary_row, "Below Threshold (< 75%)", str(summary.students_below_threshold),
                             "warning").grid(row=0, column=1, sticky="nsew", padx=8, pady=(0, 10))
        self._summary_card(summary_row, "Critically Below (< 65%)", str(summary.students_critically_below_threshold),
                             "danger").grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=(0, 10))

        # Filters
        filter_wrap = tk.Frame(self, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        filter_wrap.pack(fill="x", padx=PADDING["xl"])
        departments = ["All"] + student_service.get_departments()
        semesters = ["All"] + [str(i) for i in range(1, 9)]
        sections = ["All"] + student_service.get_sections()
        subjects = ["All"] + attendance_service.get_all_subjects()
        statuses = ["All", "Healthy", "Below Threshold", "Critical"]

        self.filter_bar = FilterBar(
            filter_wrap,
            filters=[
                ("department", "Department", departments),
                ("semester", "Semester", semesters),
                ("section", "Section", sections),
                ("subject", "Subject", subjects),
                ("status", "Status", statuses),
            ],
            on_change=self._apply_filters,
        )
        self.filter_bar.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])

        self.table_holder = tk.Frame(self, bg=COLORS["bg"])
        self.table_holder.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(10, PADDING["lg"]))

        self._apply_filters(self.filter_bar.get_values())

    def _summary_card(self, parent, label, value, accent):
        from ui.components import KPICard
        return KPICard(parent, label, value, accent)

    def _apply_filters(self, values):
        for w in self.table_holder.winfo_children():
            w.destroy()

        records = attendance_service.get_attendance(
            department=values.get("department", "All"),
            semester=values.get("semester", "All"),
            section=values.get("section", "All"),
            subject=values.get("subject", "All"),
            status=values.get("status", "All"),
            search=values.get("search", ""),
        )

        if not records:
            StatePlaceholder(self.table_holder, "No attendance records match the selected filters.",
                               kind="empty").pack(fill="both", expand=True)
            return

        columns = [
            ("student_id", "Student ID", 90, "w"),
            ("student_name", "Name", 150, "w"),
            ("subject", "Subject", 180, "w"),
            ("classes_held", "Held", 60, "center"),
            ("present", "Present", 65, "center"),
            ("absent", "Absent", 65, "center"),
            ("percentage", "%", 70, "center"),
            ("status", "Status", 130, "center"),
        ]
        table = DataTable(self.table_holder, columns, height=17)
        table.pack(fill="both", expand=True)

        rows = []
        for r in records:
            rows.append(dict(
                student_id=r.student_id, student_name=r.student_name, subject=r.subject,
                classes_held=r.classes_held, present=r.present, absent=r.absent,
                percentage=f"{r.percentage}%", status=_attendance_status(r.percentage).title(),
                _raw=r,
            ))
        table.set_rows(rows)

        tk.Label(self.table_holder, text=f"{len(records)} record(s) found", font=FONTS["small"],
                  fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(anchor="w", pady=(6, 0))
