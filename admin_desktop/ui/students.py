"""Student Management — searchable/filterable directory + detail drill-down."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, PADDING
from services import student_service
from ui.components import DataTable, FilterBar, StatePlaceholder, Card, status_badge
from utils.formatters import format_percentage, format_date_display


class StudentsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._show_list()

    # ------------------------------------------------------------------
    # List view
    # ------------------------------------------------------------------
    def _show_list(self):
        for w in self.winfo_children():
            w.destroy()

        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Students", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        filter_wrap = tk.Frame(self, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        filter_wrap.pack(fill="x", padx=PADDING["xl"])
        departments = ["All"] + student_service.get_departments()
        semesters = ["All"] + [str(i) for i in range(1, 9)]
        sections = ["All"] + student_service.get_sections()
        statuses = ["All", "ACTIVE", "INACTIVE"]

        self.filter_bar = FilterBar(
            filter_wrap,
            filters=[
                ("department", "Department", departments),
                ("semester", "Semester", semesters),
                ("section", "Section", sections),
                ("status", "Status", statuses),
            ],
            on_change=self._apply_filters,
        )
        self.filter_bar.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])

        self.table_holder = tk.Frame(self, bg=COLORS["bg"])
        self.table_holder.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(10, PADDING["lg"]))

        self._apply_filters(self.filter_bar.get_values())

    def _apply_filters(self, values):
        for w in self.table_holder.winfo_children():
            w.destroy()

        students = student_service.get_students(
            search=values.get("search", ""),
            department=values.get("department", "All"),
            semester=values.get("semester", "All"),
            section=values.get("section", "All"),
            status=values.get("status", "All"),
        )

        if not students:
            StatePlaceholder(self.table_holder, "No students match the selected filters.",
                               kind="empty").pack(fill="both", expand=True)
            return

        columns = [
            ("student_id", "Student ID", 90, "w"),
            ("name", "Name", 160, "w"),
            ("roll_number", "Roll Number", 110, "w"),
            ("department", "Department", 190, "w"),
            ("semester", "Sem", 50, "center"),
            ("section", "Sec", 50, "center"),
            ("email", "Email", 200, "w"),
            ("status", "Status", 90, "center"),
        ]
        table = DataTable(self.table_holder, columns, on_row_activate=self._open_detail, height=18)
        table.pack(fill="both", expand=True)

        rows = [dict(student_id=s.student_id, name=s.name, roll_number=s.roll_number,
                       department=s.department, semester=s.semester, section=s.section,
                       email=s.email, status=s.status, _raw=s) for s in students]
        table.set_rows(rows)

        count_label = tk.Label(self.table_holder, text=f"{len(students)} student(s) found",
                                 font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["bg"])
        count_label.pack(anchor="w", pady=(6, 0))

    def _open_detail(self, row):
        student = row["_raw"]
        self._show_detail(student.student_id)

    # ------------------------------------------------------------------
    # Detail view
    # ------------------------------------------------------------------
    def _show_detail(self, student_id):
        for w in self.winfo_children():
            w.destroy()

        detail = student_service.get_student_details(student_id)
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        ttk.Button(header, text="← Back to Students", style="Secondary.TButton",
                    command=self._show_list).pack(side="left")

        if not detail:
            StatePlaceholder(self, "Student record not found.", kind="error").pack(fill="both", expand=True)
            return

        s = detail.student
        tk.Label(header, text=f"  {s.name}", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left", padx=(12, 0))
        status_badge(header, s.status).pack(side="left", padx=(10, 0))

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(8, PADDING["lg"]))
        body.grid_columnconfigure(0, weight=1, uniform="c")
        body.grid_columnconfigure(1, weight=1, uniform="c")

        # Personal info card
        info_card = Card(body, title="Personal Information")
        info_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        for label, value in [
            ("Student ID", s.student_id), ("Roll Number", s.roll_number),
            ("Email", s.email), ("Phone", s.phone or "—"),
            ("Department", s.department), ("Semester", str(s.semester)),
            ("Section", s.section), ("Admission Year", str(s.admission_year)),
        ]:
            self._info_row(info_card.body, label, value)

        # Academic overview card
        academic_card = Card(body, title="Academic Overview")
        academic_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        warn_color = COLORS["danger"] if detail.attendance_warning else COLORS["success"]
        tk.Label(academic_card.body, text="Overall Attendance", font=FONTS["small_bold"],
                  fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
        tk.Label(academic_card.body, text=format_percentage(detail.overall_attendance),
                  font=FONTS["kpi_value"], fg=warn_color, bg=COLORS["surface"]).pack(anchor="w", pady=(0, 4))
        if detail.attendance_warning:
            tk.Label(academic_card.body, text="⚠ Attendance below warning threshold",
                      font=FONTS["small"], fg=COLORS["danger"], bg=COLORS["surface"]).pack(anchor="w", pady=(0, 8))

        for rec in detail.subject_attendance:
            row = tk.Frame(academic_card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=rec.subject, font=FONTS["small"], fg=COLORS["text"],
                      bg=COLORS["surface"]).pack(side="left")
            tk.Label(row, text=f"{rec.present}/{rec.classes_held} · {format_percentage(rec.percentage)}",
                      font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(side="right")
        if not detail.subject_attendance:
            tk.Label(academic_card.body, text="No attendance records available.", font=FONTS["small"],
                      fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")

        # Gate-pass summary card
        gp_card = Card(body, title="Gate-Pass Summary")
        gp_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        gp = detail.gatepass_summary
        stats_row = tk.Frame(gp_card.body, bg=COLORS["surface"])
        stats_row.pack(fill="x")
        for label, value, color in [
            ("Total", gp.total, "text"), ("Approved", gp.approved, "success"),
            ("Rejected", gp.rejected, "danger"), ("Pending", gp.pending, "warning"),
        ]:
            cell = tk.Frame(stats_row, bg=COLORS["surface"])
            cell.pack(side="left", expand=True, fill="x")
            tk.Label(cell, text=str(value), font=FONTS["h3"], fg=COLORS[color], bg=COLORS["surface"]).pack()
            tk.Label(cell, text=label, font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["surface"]).pack()

        # Recent activity card
        activity_card = Card(body, title="Recent Gate-Pass Requests")
        activity_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        if not detail.recent_gatepasses:
            tk.Label(activity_card.body, text="No recent gate-pass requests.", font=FONTS["small"],
                      fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
        for g in detail.recent_gatepasses:
            row = tk.Frame(activity_card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=3)
            top = tk.Frame(row, bg=COLORS["surface"])
            top.pack(fill="x")
            tk.Label(top, text=f"{g.destination} · {format_date_display(g.departure_date)}",
                      font=FONTS["small"], fg=COLORS["text"], bg=COLORS["surface"]).pack(side="left")
            status_badge(top, g.status).pack(side="right")

    def _info_row(self, parent, label, value):
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=FONTS["small"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"], width=16, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=FONTS["small_bold"], fg=COLORS["text"],
                  bg=COLORS["surface"], anchor="w").pack(side="left", fill="x", expand=True)
