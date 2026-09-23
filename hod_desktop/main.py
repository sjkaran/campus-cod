"""
Entry point for the HOD Desktop Application (Stage 1 — UI prototype
with a mock data layer; see api/api_client.py for the Stage 2
integration boundary).

Run with:
    python main.py
"""

import tkinter as tk
from tkinter import ttk

from config.settings import APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from ui.theme import apply_theme
from ui.login import LoginScreen


class HODDesktopApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")

        apply_theme(self.root)

        self.current_screen = None
        self._show_login()

    def _show_login(self):
        self._clear_current_screen()
        self.current_screen = LoginScreen(self.root, on_login_success=self._show_app)

    def _show_app(self, hod_profile):
        from ui.app import HODApp
        self._clear_current_screen()
        self.current_screen = HODApp(self.root, hod_profile, on_logout=self._show_login)

    def _clear_current_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    HODDesktopApplication().run()
