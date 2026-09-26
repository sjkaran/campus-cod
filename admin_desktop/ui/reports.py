"""Reports — parameterized report generation with preview and export (Stage 1 mock)."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, PADDING
from services import report_service, student_service
from ui.components import Card, DataTable, StatePlaceholder, info_dialog


class ReportsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Reports", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(0, PADDING["lg"]))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        params_card = Card(body, title="Report Parameters")
        params_card.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        form = params_card.body

        tk.Label(form, text="Report Type", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.type_var = tk.StringVar(value=report_service.REPORT_TYPES[0])
        ttk.Combobox(form, textvariable=self.type_var, values=report_service.REPORT_TYPES,
                      state="readonly", width=32, style="Admin.TCombobox").pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Department", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.dept_var = tk.StringVar(value="All")
        ttk.Combobox(form, textvariable=self.dept_var,
                      values=["All"] + student_service.get_departments(),
                      state="readonly", width=32, style="Admin.TCombobox").pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Semester", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.sem_var = tk.StringVar(value="All")
        ttk.Combobox(form, textvariable=self.sem_var,
                      values=["All"] + [str(i) for i in range(1, 9)],
                      state="readonly", width=32, style="Admin.TCombobox").pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Section", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.section_var = tk.StringVar(value="All")
        ttk.Combobox(form, textvariable=self.section_var,
                      values=["All"] + student_service.get_sections(),
                      state="readonly", width=32, style="Admin.TCombobox").pack(fill="x", pady=(4, 16))

        btn_row = tk.Frame(form, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Generate", style="Primary.TButton", command=self._generate).pack(fill="x")
        ttk.Button(btn_row, text="Export (CSV)", style="Secondary.TButton",
                    command=self._export).pack(fill="x", pady=(8, 0))

        self.result_holder = tk.Frame(body, bg=COLORS["bg"])
        self.result_holder.grid(row=0, column=1, sticky="nsew")
        StatePlaceholder(self.result_holder, "Choose parameters and click Generate to preview a report.",
                           kind="empty").pack(fill="both", expand=True)

        self._last_result = None

    def _generate(self):
        for w in self.result_holder.winfo_children():
            w.destroy()

        result = report_service.generate_report(
            report_type=self.type_var.get(),
            department=self.dept_var.get(),
            semester=self.sem_var.get(),
            section=self.section_var.get(),
        )
        self._last_result = result

        if not result.rows:
            StatePlaceholder(self.result_holder, "No data available for the selected parameters.",
                               kind="empty").pack(fill="both", expand=True)
            return

        meta = tk.Frame(self.result_holder, bg=COLORS["bg"])
        meta.pack(fill="x", pady=(0, 8))
        tk.Label(meta, text=f"{result.title}  ·  {result.row_count} row(s)  ·  generated {result.generated_on}",
                  font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(anchor="w")

        columns = [(str(i), col, 140, "w") for i, col in enumerate(result.columns)]
        table = DataTable(self.result_holder, columns, height=17)
        table.pack(fill="both", expand=True)
        rows = [{str(i): val for i, val in enumerate(row)} for row in result.rows]
        table.set_rows(rows)

    def _export(self):
        if not self._last_result:
            info_dialog(self.app.root, "Nothing to Export", "Generate a report first, then export it.")
            return
        info_dialog(
            self.app.root, "Export Report",
            f'"{self._last_result.title}" would be exported to CSV/PDF here once the backend '
            f'report-generation endpoint (GET /api/reports/...) is connected in Stage 2.',
        )
