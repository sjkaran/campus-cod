"""Screen 4 — Notifications: publish new, view previously published."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

from config.settings import Colors, Fonts
from services import notification_service
from ui.widgets import Card, StatusBadge, EmptyState, SectionHeader, make_table, error_dialog, info_dialog
from utils.helpers import is_valid_date


class NotificationsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        self._build()

    def _build(self):
        header = SectionHeader(self, "Notifications", "Publish departmental announcements")
        header.pack(fill="x")

        body = ttk.Frame(self, style="App.TFrame")
        body.pack(fill="both", expand=True, pady=(16, 0))
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_history(body)

    # ------------------------------------------------------------------
    def _build_form(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(card, text="Publish New Notification", style="H2Card.TLabel").pack(anchor="w", pady=(0, 12))

        ttk.Label(card, text="Title", style="Card.TLabel").pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.title_var, style="App.TEntry").pack(fill="x", pady=(4, 12))

        ttk.Label(card, text="Message", style="Card.TLabel").pack(anchor="w")
        self.message_text = tk.Text(card, height=5, font=Fonts.BODY, wrap="word",
                                     relief="solid", borderwidth=1)
        self.message_text.pack(fill="x", pady=(4, 12))

        ttk.Label(card, text="Audience", style="Card.TLabel").pack(anchor="w")
        self.audience_var = tk.StringVar(value="Department")
        audience_combo = ttk.Combobox(
            card, textvariable=self.audience_var, state="readonly", style="App.TCombobox",
            values=notification_service.VALID_AUDIENCES,
        )
        audience_combo.pack(fill="x", pady=(4, 12))

        ttk.Label(card, text="Priority", style="Card.TLabel").pack(anchor="w")
        self.priority_var = tk.StringVar(value="Normal")
        priority_combo = ttk.Combobox(
            card, textvariable=self.priority_var, state="readonly", style="App.TCombobox",
            values=notification_service.VALID_PRIORITIES,
        )
        priority_combo.pack(fill="x", pady=(4, 12))

        ttk.Label(card, text="Expiration Date (YYYY-MM-DD)", style="Card.TLabel").pack(anchor="w")
        default_expiry = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.expiry_var = tk.StringVar(value=default_expiry)
        ttk.Entry(card, textvariable=self.expiry_var, style="App.TEntry").pack(fill="x", pady=(4, 4))

        self.error_lbl = tk.Label(card, text="", fg=Colors.DANGER, bg=Colors.CARD_BG,
                                   font=Fonts.SMALL, wraplength=320, justify="left")
        self.error_lbl.pack(anchor="w", pady=(6, 0))

        btn_row = ttk.Frame(card, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(16, 0))
        ttk.Button(btn_row, text="Clear", style="Secondary.TButton",
                   command=self._clear_form).pack(side="right", padx=(8, 0))
        ttk.Button(btn_row, text="Publish", style="Primary.TButton",
                   command=self._publish).pack(side="right")

    def _clear_form(self):
        self.title_var.set("")
        self.message_text.delete("1.0", "end")
        self.audience_var.set("Department")
        self.priority_var.set("Normal")
        self.expiry_var.set((datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.error_lbl.configure(text="")

    def _publish(self):
        self.error_lbl.configure(text="")
        message = self.message_text.get("1.0", "end").strip()
        expiry = self.expiry_var.get().strip()

        if expiry and not is_valid_date(expiry):
            self.error_lbl.configure(text="Expiration date must be in YYYY-MM-DD format.")
            return

        try:
            notification_service.publish_notification(
                self.title_var.get(), message, self.audience_var.get(),
                self.priority_var.get(), expiry,
            )
        except ValueError as e:
            self.error_lbl.configure(text=str(e))
            return

        info_dialog(self, "Published", "Notification published successfully.")
        self._clear_form()
        self._refresh_history()

    # ------------------------------------------------------------------
    def _build_history(self, parent):
        card = Card(parent, padding=(0, 0))
        card.grid(row=0, column=1, sticky="nsew")
        card.configure(borderwidth=1, relief="solid")

        self.history_holder = ttk.Frame(card, style="Card.TFrame")
        self.history_holder.pack(fill="both", expand=True, padx=16, pady=16)
        self._refresh_history()

    def _refresh_history(self):
        for child in self.history_holder.winfo_children():
            child.destroy()

        ttk.Label(self.history_holder, text="Previously Published", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))

        notifications = notification_service.get_my_notifications()
        if not notifications:
            EmptyState(self.history_holder, "No notifications published yet.", icon="🔔").pack(fill="both", expand=True)
            return

        columns = [
            ("title", "Title", 220, "w"),
            ("audience", "Audience", 130, "w"),
            ("created", "Created", 130, "center"),
            ("status", "Status", 90, "center"),
        ]
        container, tree = make_table(self.history_holder, columns, height=13)
        container.pack(fill="both", expand=True)
        for n in notifications:
            tree.insert("", "end", values=(n.title, n.audience, n.created_at, n.status))
