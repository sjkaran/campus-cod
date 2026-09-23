"""Screen 5 — Attendance viewing with filters."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts
from services import attendance_service
from ui.widgets import Card, EmptyState, SectionHeader, make_table
from utils.helpers import attendance_label, attendance_band


class AttendanceScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        self.options = attendance_service.get_filter_options()
        self._build()

    def _build(self):
        header = SectionHeader(self, "Attendance", "View and filter departmental attendance records")
        header.pack(fill="x")

        filter_card = Card(self)
        filter_card.pack(fill="x", pady=(16, 12))

        row = ttk.Frame(filter_card, style="Card.TFrame")
        row.pack(fill="x")

        self.sem_var = tk.StringVar(value="All")
        self.section_var = tk.StringVar(value="All")
        self.subject_var = tk.StringVar(value="All")

        self._filter_field(row, "Semester", self.sem_var, ["All"] + [str(s) for s in self.options["semesters"]])
        self._filter_field(row, "Section", self.section_var, ["All"] + self.options["sections"])
        self._filter_field(row, "Subject", self.subject_var, ["All"] + self.options["subjects"])

        ttk.Button(row, text="Apply Filters", style="Primary.TButton",
                   command=self._refresh_table).pack(side="left", padx=(16, 0), pady=(18, 0))
        ttk.Button(row, text="Reset", style="Secondary.TButton",
                   command=self._reset_filters).pack(side="left", padx=(8, 0), pady=(18, 0))

        legend = ttk.Frame(self, style="App.TFrame")
        legend.pack(fill="x", pady=(0, 8))
        self._legend_item(legend, "Good (90%+)", Colors.ATTN_GOOD)
        self._legend_item(legend, "Normal (75-89%)", Colors.ATTN_NORMAL)
        self._legend_item(legend, "Attention (<75%)", Colors.ATTN_LOW)

        table_card = Card(self, padding=(0, 0))
        table_card.pack(fill="both", expand=True)
        table_card.configure(borderwidth=1, relief="solid")
        self.table_holder = ttk.Frame(table_card, style="Card.TFrame")
        self.table_holder.pack(fill="both", expand=True, padx=16, pady=16)

        self._refresh_table()

    def _filter_field(self, parent, label, var, values):
        col = ttk.Frame(parent, style="Card.TFrame")
        col.pack(side="left", padx=(0, 16))
        ttk.Label(col, text=label, style="Card.TLabel").pack(anchor="w")
        combo = ttk.Combobox(col, textvariable=var, values=values, state="readonly",
                              style="App.TCombobox", width=16)
        combo.pack(anchor="w", pady=(4, 0))

    def _legend_item(self, parent, text, color):
        item = ttk.Frame(parent, style="App.TFrame")
        item.pack(side="left", padx=(0, 16))
        tk.Label(item, text="●", fg=color, bg=Colors.BG, font=Fonts.BODY_BOLD).pack(side="left")
        ttk.Label(item, text=text, style="Muted.TLabel").pack(side="left", padx=(4, 0))

    def _reset_filters(self):
        self.sem_var.set("All")
        self.section_var.set("All")
        self.subject_var.set("All")
        self._refresh_table()

    def _refresh_table(self):
        for child in self.table_holder.winfo_children():
            child.destroy()

        records = attendance_service.get_department_attendance(
            semester=self.sem_var.get(), section=self.section_var.get(),
            subject=self.subject_var.get(),
        )

        if not records:
            EmptyState(self.table_holder, "No attendance records match these filters.", icon="📋").pack(
                fill="both", expand=True
            )
            return

        columns = [
            ("student_id", "Student ID", 90, "w"),
            ("name", "Student Name", 150, "w"),
            ("subject", "Subject", 150, "w"),
            ("held", "Classes Held", 90, "center"),
            ("present", "Present", 80, "center"),
            ("absent", "Absent", 80, "center"),
            ("pct", "Attendance %", 100, "center"),
            ("status", "Status", 90, "center"),
        ]
        container, tree = make_table(self.table_holder, columns, height=14)
        container.pack(fill="both", expand=True)

        tree.tag_configure("good", foreground=Colors.ATTN_GOOD)
        tree.tag_configure("normal", foreground=Colors.ATTN_NORMAL)
        tree.tag_configure("attention", foreground=Colors.ATTN_LOW)

        for r in records:
            band = attendance_band(r.percentage)
            tree.insert("", "end", values=(
                r.student_id, r.student_name, r.subject, r.classes_held,
                r.present, r.absent, f"{r.percentage}%", attendance_label(r.percentage),
            ), tags=(band,))

        summary = ttk.Frame(self.table_holder, style="Card.TFrame")
        summary.pack(fill="x", pady=(10, 0))
        ttk.Label(summary, text=f"{len(records)} record(s) shown", style="CardMuted.TLabel").pack(anchor="w")
