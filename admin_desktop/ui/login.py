"""Admin login screen: credentials form, validation, loading & error states."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, APP_NAME, MOCK_ADMIN_CREDENTIALS
from services.auth_service import authenticate_admin
from utils.validators import validate_login_form


class LoginScreen(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=COLORS["bg"])
        self.on_login_success = on_login_success
        self._building = False
        self._build()

    def _build(self):
        # Center card
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(outer, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, padx=40, pady=36)
        card.pack()

        # Brand header
        tk.Label(card, text="🎓", font=(FONTS["h1"][0], 30), bg=COLORS["surface"]).pack()
        tk.Label(card, text=APP_NAME, font=FONTS["h1"], fg=COLORS["text"],
                  bg=COLORS["surface"]).pack(pady=(6, 0))
        tk.Label(card, text="Administrator Sign In", font=FONTS["body"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(pady=(2, 24))

        form = tk.Frame(card, bg=COLORS["surface"])
        form.pack(fill="x")

        tk.Label(form, text="Admin ID / Username", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form, textvariable=self.username_var, width=34, style="Admin.TEntry")
        username_entry.pack(fill="x", pady=(4, 14))
        username_entry.focus_set()

        tk.Label(form, text="Password", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")

        pw_row = tk.Frame(form, bg=COLORS["surface"])
        pw_row.pack(fill="x", pady=(4, 4))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(pw_row, textvariable=self.password_var, width=28,
                                          show="•", style="Admin.TEntry")
        self.password_entry.pack(side="left", fill="x", expand=True)
        self._show_password = False
        self.toggle_btn = ttk.Button(pw_row, text="Show", width=6, style="Secondary.TButton",
                                       command=self._toggle_password)
        self.toggle_btn.pack(side="left", padx=(6, 0))

        self.error_label = tk.Label(form, text="", font=FONTS["small"], fg=COLORS["danger"],
                                      bg=COLORS["surface"], wraplength=280, justify="left")
        self.error_label.pack(anchor="w", pady=(10, 0))

        self.login_btn = ttk.Button(form, text="Login", style="Primary.TButton", command=self._attempt_login)
        self.login_btn.pack(fill="x", pady=(18, 0))

        self.status_label = tk.Label(form, text="", font=FONTS["small"], fg=COLORS["text_muted"],
                                       bg=COLORS["surface"])
        self.status_label.pack(pady=(10, 0))

        hint = ", ".join(f"{u} / {p}" for u, p in MOCK_ADMIN_CREDENTIALS.items())
        tk.Label(card, text=f"Stage 1 demo credentials — {hint}", font=FONTS["small"],
                  fg=COLORS["text_subtle"], bg=COLORS["surface"], wraplength=320,
                  justify="center").pack(pady=(18, 0))

        self.bind_all("<Return>", lambda _e: self._attempt_login())

    def _toggle_password(self):
        self._show_password = not self._show_password
        self.password_entry.config(show="" if self._show_password else "•")
        self.toggle_btn.config(text="Hide" if self._show_password else "Show")

    def _attempt_login(self):
        if self._building:
            return
        username = self.username_var.get()
        password = self.password_var.get()

        errors = validate_login_form(username, password)
        if errors:
            self.error_label.config(text=errors[0])
            return

        self.error_label.config(text="")
        self._set_loading(True)
        # Simulated async login — Stage 2 would await a network call here.
        self.after(450, lambda: self._finish_login(username, password))

    def _finish_login(self, username, password):
        result = authenticate_admin(username, password)
        self._set_loading(False)
        if not result.success:
            self.error_label.config(text=result.error or "Invalid Admin ID or password.")
            return
        self.on_login_success(result.admin)

    def _set_loading(self, loading: bool):
        self._building = loading
        self.login_btn.config(state="disabled" if loading else "normal")
        self.status_label.config(text="Signing in…" if loading else "")
