"""Settings — Admin profile, application info, session info (Stage 1 read-only)."""

import tkinter as tk

from config.settings import COLORS, FONTS, PADDING, APP_NAME, APP_VERSION
from ui.components import Card
from utils.helpers import now_str


class SettingsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Settings", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(0, PADDING["lg"]))
        body.grid_columnconfigure(0, weight=1, uniform="c")
        body.grid_columnconfigure(1, weight=1, uniform="c")

        admin = self.app.admin

        profile_card = Card(body, title="Admin Profile")
        profile_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        for label, value in [
            ("Admin ID", admin.admin_id), ("Name", admin.name),
            ("Username", admin.username), ("Designation", admin.designation),
            ("Department", admin.department), ("Email", admin.email),
        ]:
            self._row(profile_card.body, label, value)

        session_card = Card(body, title="Session Information")
        session_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self._row(session_card.body, "Signed in as", admin.username)
        self._row(session_card.body, "Current time", now_str("%d %b %Y, %I:%M %p"))
        self._row(session_card.body, "Session type", "Stage 1 — Mock Authentication")

        app_card = Card(body, title="Application Information")
        app_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self._row(app_card.body, "Application", APP_NAME)
        self._row(app_card.body, "Version", APP_VERSION)
        self._row(app_card.body, "Node", "Admin Desktop Application")
        self._row(app_card.body, "Backend status", "Not connected (Stage 1 — mock data)")

        prefs_card = Card(body, title="Display Preferences")
        prefs_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(prefs_card.body, text="Display and notification preferences will be configurable "
                                          "once user-preference storage is introduced in a future stage.",
                  font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["surface"],
                  wraplength=320, justify="left").pack(anchor="w")

    def _row(self, parent, label, value):
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, font=FONTS["small"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"], width=16, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=FONTS["small_bold"], fg=COLORS["text"],
                  bg=COLORS["surface"], anchor="w").pack(side="left", fill="x", expand=True)
