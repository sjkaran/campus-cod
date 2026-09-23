"""Settings screen — session/profile info. Kept intentionally minimal:
the HOD role has no admin-level configuration access."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts, APP_VERSION, DATA_SOURCE_MODE
from ui.widgets import Card, SectionHeader


class SettingsScreen(ttk.Frame):
    def __init__(self, parent, hod_profile):
        super().__init__(parent, style="App.TFrame")
        self.hod_profile = hod_profile
        self._build()

    def _build(self):
        header = SectionHeader(self, "Settings", "Session and account information")
        header.pack(fill="x")

        card = Card(self)
        card.pack(fill="x", pady=(16, 0), anchor="n")

        ttk.Label(card, text="Profile", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))
        self._row(card, "Name", self.hod_profile["name"])
        self._row(card, "HOD ID", self.hod_profile["hod_id"])
        self._row(card, "Department", self.hod_profile["department"])
        self._row(card, "Designation", self.hod_profile["designation"])

        ttk.Separator(card, style="App.Horizontal.TSeparator").pack(fill="x", pady=14)

        ttk.Label(card, text="About", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))
        self._row(card, "Application", "HOD Desktop Portal")
        self._row(card, "Version", APP_VERSION)
        self._row(card, "Data source", "Mock (Stage 1)" if DATA_SOURCE_MODE == "mock" else "Live API")

        note = ttk.Label(
            card,
            text="Note: this application does not have administrator-level access. "
                 "All permissions are enforced by the central backend once integrated.",
            style="CardMuted.TLabel", wraplength=420, justify="left",
        )
        note.pack(anchor="w", pady=(16, 0))

    def _row(self, parent, label, value):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED, font=Fonts.SMALL,
                 width=14, anchor="w").pack(side="left")
        tk.Label(row, text=value, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, font=Fonts.BODY,
                 anchor="w").pack(side="left")
