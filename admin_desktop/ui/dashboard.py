"""Admin Dashboard — high-level campus overview with KPI cards and recents."""

import tkinter as tk

from config.settings import COLORS, FONTS, PADDING
from services.dashboard_service import get_dashboard_data
from ui.components import KPICard, Card, status_badge, StatePlaceholder
from utils.formatters import format_number, format_percentage, format_date_display


class DashboardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._render_loading()
        self.after(200, self._load)

    def _render_loading(self):
        for w in self.winfo_children():
            w.destroy()
        StatePlaceholder(self, "Loading dashboard…", kind="loading").pack(fill="both", expand=True)

    def _load(self):
        try:
            data = get_dashboard_data()
        except Exception:
            for w in self.winfo_children():
                w.destroy()
            StatePlaceholder(self, "Unable to load dashboard data.", kind="error",
                               on_retry=self._reload).pack(fill="both", expand=True)
            return
        self._render(data)

    def _reload(self):
        self._render_loading()
        self.after(200, self._load)

    def _render(self, data):
        for w in self.winfo_children():
            w.destroy()

        scroll_holder = tk.Frame(self, bg=COLORS["bg"])
        scroll_holder.pack(fill="both", expand=True, padx=PADDING["xl"], pady=PADDING["lg"])

        tk.Label(scroll_holder, text="Campus Overview", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(anchor="w", pady=(0, 12))

        # KPI grid
        kpi_row1 = tk.Frame(scroll_holder, bg=COLORS["bg"])
        kpi_row1.pack(fill="x")
        for i in range(4):
            kpi_row1.grid_columnconfigure(i, weight=1, uniform="kpi")

        KPICard(kpi_row1, "Total Students", format_number(data.total_students), "primary",
                 subtitle=f"{format_number(data.active_students)} active").grid(
            row=0, column=0, sticky="nsew", padx=(0, 10), pady=4)
        KPICard(kpi_row1, "Average Attendance", format_percentage(data.average_attendance), "success").grid(
            row=0, column=1, sticky="nsew", padx=10, pady=4)
        KPICard(kpi_row1, "Pending Gate Passes", format_number(data.pending_gatepasses), "warning").grid(
            row=0, column=2, sticky="nsew", padx=10, pady=4)
        KPICard(kpi_row1, "Today's Presence", format_percentage(data.todays_attendance), "info").grid(
            row=0, column=3, sticky="nsew", padx=(10, 0), pady=4)

        kpi_row2 = tk.Frame(scroll_holder, bg=COLORS["bg"])
        kpi_row2.pack(fill="x", pady=(4, 16))
        kpi_row2.grid_columnconfigure(0, weight=1)
        KPICard(kpi_row2, "Notifications Published", format_number(data.notifications_published), "primary").grid(
            row=0, column=0, sticky="w")

        # Two-column area: notifications + gate-pass activity
        columns = tk.Frame(scroll_holder, bg=COLORS["bg"])
        columns.pack(fill="both", expand=True)
        columns.grid_columnconfigure(0, weight=1, uniform="col")
        columns.grid_columnconfigure(1, weight=1, uniform="col")

        notif_card = Card(columns, title="Recent Notifications")
        notif_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        if not data.recent_notifications:
            tk.Label(notif_card.body, text="No active notifications.", font=FONTS["small"],
                      fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
        for n in data.recent_notifications:
            row = tk.Frame(notif_card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=5)
            top = tk.Frame(row, bg=COLORS["surface"])
            top.pack(fill="x")
            tk.Label(top, text=n.title, font=FONTS["small_bold"], fg=COLORS["text"],
                      bg=COLORS["surface"]).pack(side="left")
            status_badge(top, n.priority).pack(side="right")
            tk.Label(row, text=f"{n.audience_detail} · {format_date_display(n.published_date)}",
                      font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")

        gp_card = Card(columns, title="Recent Gate-Pass Activity")
        gp_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        if not data.recent_gatepasses:
            tk.Label(gp_card.body, text="No gate-pass activity.", font=FONTS["small"],
                      fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
        for g in data.recent_gatepasses:
            row = tk.Frame(gp_card.body, bg=COLORS["surface"])
            row.pack(fill="x", pady=5)
            top = tk.Frame(row, bg=COLORS["surface"])
            top.pack(fill="x")
            tk.Label(top, text=f"{g.student_name} → {g.destination}", font=FONTS["small_bold"],
                      fg=COLORS["text"], bg=COLORS["surface"]).pack(side="left")
            status_badge(top, g.status).pack(side="right")
            tk.Label(row, text=f"{g.department} · Submitted {format_date_display(g.submitted_date)}",
                      font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["surface"]).pack(anchor="w")
