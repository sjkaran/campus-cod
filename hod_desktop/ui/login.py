"""Screen 1 — HOD Login."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts, APP_NAME
from services import auth_service
from services.auth_service import AuthError
from ui.widgets import error_dialog


class LoginScreen(ttk.Frame):
    """
    Renders full-window until login succeeds, then calls
    on_login_success(hod_profile) so main.py can swap to the app shell.
    """

    def __init__(self, parent, on_login_success):
        super().__init__(parent, style="App.TFrame")
        self.on_login_success = on_login_success
        self._password_visible = False
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        wrapper = ttk.Frame(self, style="App.TFrame")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        card = ttk.Frame(wrapper, style="Card.TFrame", padding=(40, 36), borderwidth=1, relief="solid")
        card.pack()

        tk.Label(card, text="Smart Campus", font=(Fonts.FAMILY, 22, "bold"),
                 fg=Colors.PRIMARY, bg=Colors.CARD_BG).pack(anchor="w")
        ttk.Label(card, text="HOD Portal — Department Access", style="CardMuted.TLabel").pack(
            anchor="w", pady=(2, 24)
        )

        ttk.Label(card, text="HOD ID / Username", style="Card.TLabel").pack(anchor="w")
        self.id_var = tk.StringVar()
        id_entry = ttk.Entry(card, textvariable=self.id_var, style="App.TEntry", width=34)
        id_entry.pack(anchor="w", pady=(4, 14))
        id_entry.focus_set()

        ttk.Label(card, text="Password", style="Card.TLabel").pack(anchor="w")
        pw_row = ttk.Frame(card, style="Card.TFrame")
        pw_row.pack(anchor="w", pady=(4, 4), fill="x")

        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(pw_row, textvariable=self.pw_var, style="App.TEntry",
                                   width=28, show="•")
        self.pw_entry.pack(side="left")

        self.toggle_btn = ttk.Button(pw_row, text="Show", style="Secondary.TButton",
                                      command=self._toggle_password, width=6)
        self.toggle_btn.pack(side="left", padx=(6, 0))

        self.error_lbl = tk.Label(card, text="", fg=Colors.DANGER, bg=Colors.CARD_BG, font=Fonts.SMALL)
        self.error_lbl.pack(anchor="w", pady=(10, 0))

        login_btn = ttk.Button(card, text="Login", style="Primary.TButton",
                                command=self._attempt_login)
        login_btn.pack(fill="x", pady=(16, 0))

        ttk.Label(card, text="Demo credentials — HOD001 / hod123", style="CardMuted.TLabel").pack(
            anchor="w", pady=(14, 0)
        )

        self.bind_all("<Return>", lambda e: self._attempt_login())

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        self.pw_entry.configure(show="" if self._password_visible else "•")
        self.toggle_btn.configure(text="Hide" if self._password_visible else "Show")

    def _attempt_login(self):
        self.error_lbl.configure(text="")
        try:
            profile = auth_service.login(self.id_var.get(), self.pw_var.get())
        except AuthError as e:
            self.error_lbl.configure(text=str(e))
            return
        self.unbind_all("<Return>")
        self.on_login_success(profile)
