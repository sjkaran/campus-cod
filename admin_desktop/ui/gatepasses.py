"""Gate-Pass Monitoring — Admin can view/filter/inspect only. Approval and
rejection belong exclusively to the HOD node's authorization model."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, PADDING
from services import gatepass_service, student_service
from ui.components import DataTable, FilterBar, StatePlaceholder, Card, status_badge
from utils.formatters import format_date_display


class GatePassesScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._show_list()

    def _show_list(self):
        for w in self.winfo_children():
            w.destroy()

        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 4))
        tk.Label(header, text="Gate Passes", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        note = tk.Label(self, text="Admin has monitoring visibility only. Approvals and rejections "
                                     "are handled by the respective Department HOD.",
                          font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["bg"])
        note.pack(anchor="w", padx=PADDING["xl"], pady=(0, 8))

        filter_wrap = tk.Frame(self, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        filter_wrap.pack(fill="x", padx=PADDING["xl"])
        departments = ["All"] + student_service.get_departments()
        statuses = ["All", "PENDING", "APPROVED", "REJECTED"]

        self.filter_bar = FilterBar(
            filter_wrap,
            filters=[
                ("department", "Department", departments),
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

        records = gatepass_service.get_gatepasses(
            department=values.get("department", "All"),
            status=values.get("status", "All"),
            search=values.get("search", ""),
        )

        if not records:
            StatePlaceholder(self.table_holder, "No gate-pass records match the selected filters.",
                               kind="empty").pack(fill="both", expand=True)
            return

        columns = [
            ("request_id", "Request ID", 90, "w"),
            ("student_id", "Student ID", 90, "w"),
            ("student_name", "Name", 150, "w"),
            ("department", "Department", 190, "w"),
            ("destination", "Destination", 110, "w"),
            ("departure_date", "Departure", 95, "center"),
            ("return_date", "Return", 95, "center"),
            ("status", "Status", 90, "center"),
        ]
        table = DataTable(self.table_holder, columns, on_row_activate=self._open_detail, height=17)
        table.pack(fill="both", expand=True)

        rows = [dict(request_id=g.request_id, student_id=g.student_id, student_name=g.student_name,
                       department=g.department, destination=g.destination,
                       departure_date=format_date_display(g.departure_date),
                       return_date=format_date_display(g.return_date), status=g.status, _raw=g)
                for g in records]
        table.set_rows(rows)

        tk.Label(self.table_holder, text=f"{len(records)} record(s) found", font=FONTS["small"],
                  fg=COLORS["text_muted"], bg=COLORS["bg"]).pack(anchor="w", pady=(6, 0))

    def _open_detail(self, row):
        self._show_detail(row["_raw"].request_id)

    def _show_detail(self, request_id):
        for w in self.winfo_children():
            w.destroy()

        gp = gatepass_service.get_gatepass_details(request_id)
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        ttk.Button(header, text="← Back to Gate Passes", style="Secondary.TButton",
                    command=self._show_list).pack(side="left")

        if not gp:
            StatePlaceholder(self, "Gate-pass record not found.", kind="error").pack(fill="both", expand=True)
            return

        tk.Label(header, text=f"  {gp.request_id}", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left", padx=(12, 0))
        status_badge(header, gp.status).pack(side="left", padx=(10, 0))

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(8, PADDING["lg"]))

        card = Card(body, title="Request Details")
        card.pack(fill="x")
        for label, value in [
            ("Student", f"{gp.student_name} ({gp.student_id})"),
            ("Department", gp.department),
            ("Destination", gp.destination),
            ("Reason", gp.reason),
            ("Departure Date", format_date_display(gp.departure_date)),
            ("Return Date", format_date_display(gp.return_date)),
            ("Submitted On", format_date_display(gp.submitted_date)),
            ("Reviewing Authority", gp.reviewing_authority),
            ("Remarks", gp.remarks or "—"),
        ]:
            row = tk.Frame(card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONTS["small"], fg=COLORS["text_muted"],
                      bg=COLORS["surface"], width=20, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=FONTS["small_bold"], fg=COLORS["text"],
                      bg=COLORS["surface"], anchor="w", wraplength=520, justify="left").pack(
                side="left", fill="x", expand=True)

        tk.Label(body, text="This record is read-only for the Admin role. Approval or rejection "
                              "must be performed by the assigned HOD.",
                  font=FONTS["small"], fg=COLORS["text_subtle"], bg=COLORS["bg"],
                  wraplength=600, justify="left").pack(anchor="w", pady=(14, 0))
