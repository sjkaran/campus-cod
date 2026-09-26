"""Persistent sidebar navigation panel."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, APP_NAME

NAV_ITEMS = [
    ("dashboard", "🏠  Dashboard"),
    ("students", "🎓  Students"),
    ("attendance", "📋  Attendance"),
    ("notifications", "📢  Notifications"),
    ("gatepasses", "🚪  Gate Passes"),
    ("analytics", "📊  Analytics"),
    ("reports", "🗎  Reports"),
    ("settings", "⚙  Settings"),
]


class Sidebar(tk.Frame):
    def __init__(self, parent, admin, on_navigate, on_logout, active_key="dashboard"):
        super().__init__(parent, bg=COLORS["sidebar_bg"], width=228)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.active_key = active_key
        self._buttons = {}

        # Brand
        brand = tk.Frame(self, bg=COLORS["sidebar_bg"])
        brand.pack(fill="x", pady=(20, 4), padx=18)
        tk.Label(brand, text="🎓 " + APP_NAME, font=FONTS["sidebar_title"],
                  fg=COLORS["sidebar_text_active"], bg=COLORS["sidebar_bg"],
                  wraplength=190, justify="left").pack(anchor="w")

        # Admin identity chip
        identity = tk.Frame(self, bg=COLORS["sidebar_bg_active"])
        identity.pack(fill="x", padx=18, pady=(14, 18))
        inner = tk.Frame(identity, bg=COLORS["sidebar_bg_active"])
        inner.pack(fill="x", padx=10, pady=8)
        tk.Label(inner, text=admin.initials, font=FONTS["body_bold"], fg=COLORS["sidebar_bg"],
                  bg=COLORS["sidebar_accent"], width=3, height=1).pack(side="left")
        text_col = tk.Frame(inner, bg=COLORS["sidebar_bg_active"])
        text_col.pack(side="left", padx=(8, 0))
        tk.Label(text_col, text=admin.name, font=FONTS["small_bold"], fg=COLORS["sidebar_text_active"],
                  bg=COLORS["sidebar_bg_active"]).pack(anchor="w")
        tk.Label(text_col, text=admin.designation, font=FONTS["small"], fg=COLORS["sidebar_text"],
                  bg=COLORS["sidebar_bg_active"]).pack(anchor="w")

        nav_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        nav_frame.pack(fill="both", expand=True)

        for key, label in NAV_ITEMS:
            btn = ttk.Button(nav_frame, text=label, style="Sidebar.TButton",
                               command=lambda k=key: self._handle_nav(k))
            btn.pack(fill="x", padx=10, pady=1)
            self._buttons[key] = btn

        self._refresh_active_styles()

        # Logout pinned to bottom
        bottom = tk.Frame(self, bg=COLORS["sidebar_bg"])
        bottom.pack(fill="x", side="bottom", pady=16, padx=10)
        ttk.Button(bottom, text="⎋  Logout", style="Sidebar.TButton",
                    command=self.on_logout).pack(fill="x")

    def _handle_nav(self, key):
        self.active_key = key
        self._refresh_active_styles()
        self.on_navigate(key)

    def _refresh_active_styles(self):
        for key, btn in self._buttons.items():
            btn.configure(style="SidebarActive.TButton" if key == self.active_key else "Sidebar.TButton")
