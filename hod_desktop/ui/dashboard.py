"""Screen 2 — HOD Dashboard."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts
from services.dashboard_service import get_dashboard_summary
from ui.widgets import StatCard, Card, EmptyState


class DashboardScreen(ttk.Frame):
    def __init__(self, parent, hod_profile, navigate_to):
        super().__init__(parent, style="App.TFrame")
        self.hod_profile = hod_profile
        self.navigate_to = navigate_to
        self._build()

    def _build(self):
        summary = get_dashboard_summary()

        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text=f"Welcome back, {self.hod_profile['name'].split(' ', 1)[-1] if ' ' in self.hod_profile['name'] else self.hod_profile['name']}",
                   style="H1.TLabel").pack(anchor="w")
        ttk.Label(header, text=f"{self.hod_profile['department']} — here's today's overview",
                   style="Muted.TLabel").pack(anchor="w", pady=(2, 20))

        # Stat cards grid
        grid = ttk.Frame(self, style="App.TFrame")
        grid.pack(fill="x")
        for i in range(4):
            grid.columnconfigure(i, weight=1, uniform="stat")

        cards = [
            ("Pending Gate Passes", summary["pending_passes"], "warning", "gatepass"),
            ("Today's Gate Passes", summary["today_passes"], "default", "gatepass"),
            ("Department Attendance", f"{summary['department_attendance']}%", "success", "attendance"),
            ("Students Below Threshold", summary["below_threshold"], "danger", "attendance"),
        ]
        for i, (label, value, tone, target) in enumerate(cards):
            card = StatCard(grid, label, value, tone=tone)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            card.bind("<Button-1>", lambda e, t=target: self.navigate_to(t))
            card.configure(cursor="hand2")

        # Two-column lower section: recent activity + recent notifications
        lower = ttk.Frame(self, style="App.TFrame")
        lower.pack(fill="both", expand=True, pady=(20, 0))
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)

        self._build_activity_panel(lower, summary["recent_activity"])
        self._build_notifications_panel(lower, summary["recent_notifications"])

    def _build_activity_panel(self, parent, activity):
        card = Card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(card, text="Recent Activity", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))

        if not activity:
            EmptyState(card, "No recent gate-pass decisions yet.", icon="🕒").pack(fill="both", expand=True)
            return

        for item in activity:
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=4)
            tk.Label(row, text="•", fg=Colors.PRIMARY, bg=Colors.CARD_BG, font=Fonts.BODY_BOLD).pack(side="left", padx=(0, 8))
            text_col = ttk.Frame(row, style="Card.TFrame")
            text_col.pack(side="left", fill="x", expand=True)
            ttk.Label(text_col, text=item["text"], style="Card.TLabel").pack(anchor="w")
            ttk.Label(text_col, text=item["timestamp"], style="CardMuted.TLabel").pack(anchor="w")

    def _build_notifications_panel(self, parent, notifications):
        card = Card(parent)
        card.grid(row=0, column=1, sticky="nsew")

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Recent Notifications", style="H2Card.TLabel").pack(side="left")
        view_all = ttk.Button(top, text="View all →", style="Secondary.TButton",
                               command=lambda: self.navigate_to("notifications"))
        view_all.pack(side="right")

        if not notifications:
            EmptyState(card, "No notifications published yet.", icon="🔔").pack(fill="both", expand=True)
            return

        for note in notifications:
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=6)
            ttk.Label(row, text=note["title"], style="Card.TLabel", font=Fonts.BODY_BOLD).pack(anchor="w")
            ttk.Label(row, text=f"{note['audience']} · {note['created_at']}", style="CardMuted.TLabel").pack(anchor="w")
