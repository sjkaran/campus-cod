"""
Application shell shown after login: header + sidebar + swappable
content area. Screens are lazily constructed and cached so navigating
back to a screen doesn't rebuild it from scratch (except gatepass,
dashboard and notifications, which refresh on every visit so approvals
etc. are reflected immediately).
"""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts, NAV_ITEMS, APP_NAME
from services import auth_service


class HODApp(ttk.Frame):
    def __init__(self, parent, hod_profile, on_logout):
        super().__init__(parent, style="App.TFrame")
        self.hod_profile = hod_profile
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.active_key = None
        self._screen_cache = {}

        self.pack(fill="both", expand=True)
        self._build_layout()
        self.show_screen("dashboard")

    # ------------------------------------------------------------------
    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_sidebar()
        self._build_content_area()

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 12))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.configure(borderwidth=0)

        bottom_border = tk.Frame(self, bg=Colors.BORDER, height=1)
        bottom_border.grid(row=0, column=0, columnspan=2, sticky="sew")

        tk.Label(header, text="Smart Campus", font=(Fonts.FAMILY, 15, "bold"),
                 fg=Colors.PRIMARY, bg=Colors.HEADER_BG).pack(side="left")
        ttk.Label(header, text="  ·  HOD Portal", style="HeaderSub.TLabel").pack(side="left")

        right = ttk.Frame(header, style="Header.TFrame")
        right.pack(side="right")

        name_frame = ttk.Frame(right, style="Header.TFrame")
        name_frame.pack(side="left", padx=(0, 4))
        ttk.Label(name_frame, text=self.hod_profile["name"], style="Header.TLabel",
                   font=Fonts.BODY_BOLD).pack(anchor="e")
        ttk.Label(name_frame, text=self.hod_profile["department"], style="HeaderSub.TLabel").pack(anchor="e")

    def _build_sidebar(self):
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=200)
        sidebar.grid(row=1, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        nav_wrap = ttk.Frame(sidebar, style="Sidebar.TFrame")
        nav_wrap.pack(fill="x", pady=(14, 0))

        for key, label in NAV_ITEMS:
            btn = ttk.Button(
                nav_wrap, text=label, style="Nav.TButton",
                command=lambda k=key: self.show_screen(k),
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_buttons[key] = btn

        spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        spacer.pack(fill="both", expand=True)

        logout_btn = ttk.Button(sidebar, text="Logout", style="Nav.TButton", command=self._logout)
        logout_btn.pack(fill="x", padx=8, pady=(0, 16), side="bottom")

    def _build_content_area(self):
        self.content = ttk.Frame(self, style="App.TFrame", padding=(24, 20))
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def show_screen(self, key):
        for child in self.content.winfo_children():
            child.grid_remove()

        if key not in self.nav_buttons:
            key = "dashboard"

        for k, btn in self.nav_buttons.items():
            btn.configure(style="NavActive.TButton" if k == key else "Nav.TButton")
        self.active_key = key

        always_fresh = {"dashboard", "gatepass", "notifications"}
        if key in always_fresh and key in self._screen_cache:
            self._screen_cache[key].destroy()
            del self._screen_cache[key]

        if key not in self._screen_cache:
            self._screen_cache[key] = self._build_screen(key)

        screen = self._screen_cache[key]
        screen.grid(row=0, column=0, sticky="nsew")

    def _build_screen(self, key):
        if key == "dashboard":
            from ui.dashboard import DashboardScreen
            return DashboardScreen(self.content, self.hod_profile, self.navigate_to)
        if key == "gatepass":
            from ui.gatepass import GatePassScreen
            return GatePassScreen(self.content, self.hod_profile)
        if key == "notifications":
            from ui.notifications import NotificationsScreen
            return NotificationsScreen(self.content)
        if key == "attendance":
            from ui.attendance import AttendanceScreen
            return AttendanceScreen(self.content)
        if key == "analytics":
            from ui.analytics import AnalyticsScreen
            return AnalyticsScreen(self.content)
        if key == "reports":
            from ui.reports import ReportsScreen
            return ReportsScreen(self.content)
        if key == "settings":
            from ui.settings import SettingsScreen
            return SettingsScreen(self.content, self.hod_profile)
        raise ValueError(f"Unknown screen: {key}")

    def navigate_to(self, key):
        """Allows child screens (e.g. dashboard cards) to change tabs."""
        self.show_screen(key)

    def _logout(self):
        from tkinter import messagebox
        if messagebox.askyesno("Log out", "Are you sure you want to log out?", parent=self):
            auth_service.logout()
            self.on_logout()
