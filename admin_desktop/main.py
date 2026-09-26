"""
Smart Campus Management System — Admin Desktop Application
Stage 1 entry point.

Run with:
    python main.py
"""

import tkinter as tk

from config.settings import APP_NAME, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, \
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLORS
from ui.theme import apply_theme
from ui.login import LoginScreen
from ui.sidebar import Sidebar
from ui.components import confirm_dialog

from ui.dashboard import DashboardScreen
from ui.students import StudentsScreen
from ui.attendance import AttendanceScreen
from ui.notifications import NotificationsScreen
from ui.gatepasses import GatePassesScreen
from ui.analytics import AnalyticsScreen
from ui.reports import ReportsScreen
from ui.settings import SettingsScreen

SCREEN_REGISTRY = {
    "dashboard": ("Dashboard", DashboardScreen),
    "students": ("Students", StudentsScreen),
    "attendance": ("Attendance", AttendanceScreen),
    "notifications": ("Notifications", NotificationsScreen),
    "gatepasses": ("Gate Passes", GatePassesScreen),
    "analytics": ("Analytics", AnalyticsScreen),
    "reports": ("Reports", ReportsScreen),
    "settings": ("Settings", SettingsScreen),
}


class AdminApp:
    """Owns the Tk root and coordinates the login -> shell transition and
    sidebar-driven screen routing. Passed to every screen as `app` so
    screens can access `app.root` and `app.admin` without global state."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.admin = None
        self.sidebar = None
        self.content_frame = None
        self.shell_frame = None

        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.configure(bg=COLORS["bg"])

        apply_theme(self.root)
        self._show_login()

    # ------------------------------------------------------------------
    def _show_login(self):
        self._clear_root()
        login_screen = LoginScreen(self.root, on_login_success=self._handle_login_success)
        login_screen.pack(fill="both", expand=True)

    def _handle_login_success(self, admin):
        self.admin = admin
        self._show_shell()

    # ------------------------------------------------------------------
    def _show_shell(self):
        self._clear_root()

        self.shell_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.shell_frame.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.shell_frame, self.admin, on_navigate=self.navigate,
                                 on_logout=self._handle_logout_request, active_key="dashboard")
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = tk.Frame(self.shell_frame, bg=COLORS["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.navigate("dashboard")

    def navigate(self, screen_key: str):
        if screen_key not in SCREEN_REGISTRY:
            return
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        _label, screen_cls = SCREEN_REGISTRY[screen_key]
        screen = screen_cls(self.content_frame, self)
        screen.pack(fill="both", expand=True)

    def _handle_logout_request(self):
        confirmed = confirm_dialog(
            self.root, "Log Out",
            "Are you sure you want to log out of the Admin application?",
            confirm_text="Log Out", danger=True,
        )
        if confirmed:
            self.admin = None
            self._show_login()

    def _clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    AdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
