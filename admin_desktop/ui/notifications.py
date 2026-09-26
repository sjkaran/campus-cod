"""Notification Management — compose/publish campus notifications, view history."""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, PADDING
from services import notification_service, student_service
from ui.components import (Card, DataTable, FilterBar, StatePlaceholder, status_badge,
                             confirm_dialog, info_dialog)
from utils.formatters import format_date_display
from utils.validators import validate_notification_form
from utils.helpers import days_from_today


class NotificationsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=PADDING["xl"], pady=(PADDING["lg"], 8))
        tk.Label(header, text="Notifications", font=FONTS["h2"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(side="left")

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PADDING["xl"], pady=(0, PADDING["lg"]))
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_composer(body)
        self._build_history(body)

    # ------------------------------------------------------------------
    def _build_composer(self, parent):
        card = Card(parent, title="Compose Notification")
        card.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        card.configure(width=340)
        form = card.body

        tk.Label(form, text="Title", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var, width=36, style="Admin.TEntry").pack(fill="x", pady=(4, 10))

        tk.Label(form, text="Message", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.message_text = tk.Text(form, height=5, width=36, font=FONTS["body"], wrap="word",
                                      relief="solid", borderwidth=1, highlightthickness=0)
        self.message_text.pack(fill="x", pady=(4, 10))

        tk.Label(form, text="Audience", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.audience_options = notification_service.get_audience_options()
        audience_labels = [label for _, label in self.audience_options]
        self.audience_var = tk.StringVar(value=audience_labels[0])
        audience_combo = ttk.Combobox(form, textvariable=self.audience_var, values=audience_labels,
                                        state="readonly", style="Admin.TCombobox")
        audience_combo.pack(fill="x", pady=(4, 10))
        audience_combo.bind("<<ComboboxSelected>>", self._on_audience_change)

        tk.Label(form, text="Audience Detail", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.detail_var = tk.StringVar(value="All Students")
        self.detail_combo = ttk.Combobox(form, textvariable=self.detail_var, values=["All Students"],
                                           state="readonly", style="Admin.TCombobox")
        self.detail_combo.pack(fill="x", pady=(4, 10))

        tk.Label(form, text="Priority", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.priority_var = tk.StringVar(value="Normal")
        ttk.Combobox(form, textvariable=self.priority_var, values=notification_service.get_priority_options(),
                      state="readonly", style="Admin.TCombobox").pack(fill="x", pady=(4, 10))

        tk.Label(form, text="Expiration Date (YYYY-MM-DD)", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.expiration_var = tk.StringVar(value=days_from_today(14))
        ttk.Entry(form, textvariable=self.expiration_var, width=36, style="Admin.TEntry").pack(fill="x", pady=(4, 6))

        self.error_label = tk.Label(form, text="", font=FONTS["small"], fg=COLORS["danger"],
                                      bg=COLORS["surface"], wraplength=300, justify="left")
        self.error_label.pack(anchor="w", pady=(4, 8))

        btn_row = tk.Frame(form, bg=COLORS["surface"])
        btn_row.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_row, text="Clear", style="Secondary.TButton", command=self._clear_form).pack(side="left")
        ttk.Button(btn_row, text="Preview", style="Secondary.TButton",
                    command=self._preview).pack(side="left", padx=8)
        ttk.Button(btn_row, text="Publish", style="Primary.TButton",
                    command=self._publish).pack(side="left")

        self._on_audience_change()

    def _on_audience_change(self, *_):
        label = self.audience_var.get()
        code = next((c for c, l in self.audience_options if l == label), "ALL_STUDENTS")
        if code == "ALL_STUDENTS":
            options = ["All Students"]
        elif code == "DEPARTMENT":
            options = student_service.get_departments()
        elif code == "SEMESTER":
            options = [f"Semester {i}" for i in range(1, 9)]
        elif code == "SECTION":
            options = [f"Section {s}" for s in student_service.get_sections()]
        else:
            options = ["Final Year Placement Group", "Hostel Residents", "Scholarship Recipients"]
        self.detail_combo.configure(values=options)
        self.detail_var.set(options[0])

    def _selected_audience_code(self) -> str:
        label = self.audience_var.get()
        return next((c for c, l in self.audience_options if l == label), "ALL_STUDENTS")

    def _clear_form(self):
        self.title_var.set("")
        self.message_text.delete("1.0", "end")
        self.audience_var.set(self.audience_options[0][1])
        self._on_audience_change()
        self.priority_var.set("Normal")
        self.expiration_var.set(days_from_today(14))
        self.error_label.config(text="")

    def _preview(self):
        title = self.title_var.get().strip() or "(No title)"
        message = self.message_text.get("1.0", "end").strip() or "(No message)"
        info_dialog(self.app.root, "Notification Preview",
                     f"{title}\n\n{message}\n\nAudience: {self.detail_var.get()}  ·  Priority: {self.priority_var.get()}")

    def _publish(self):
        title = self.title_var.get()
        message = self.message_text.get("1.0", "end")
        audience_code = self._selected_audience_code()
        audience_detail = self.detail_var.get()
        expiration = self.expiration_var.get().strip()

        errors = validate_notification_form(title, message, audience_code, "", expiration)
        if errors:
            self.error_label.config(text=errors[0])
            return
        self.error_label.config(text="")

        recipient_count = notification_service.estimate_audience_size(audience_code, audience_detail)
        confirmed = confirm_dialog(
            self.app.root, "Publish Notification",
            f'Publish "{title.strip()}" to {recipient_count:,} student(s)?',
            confirm_text="Publish",
        )
        if not confirmed:
            return

        notification_service.publish_notification(
            title=title, message=message, audience_code=audience_code,
            audience_detail=audience_detail, priority=self.priority_var.get(),
            expiration_date=expiration,
        )
        info_dialog(self.app.root, "Notification Published", "Your notification has been published successfully.")
        self._clear_form()
        self._refresh_history()

    # ------------------------------------------------------------------
    def _build_history(self, parent):
        wrap = tk.Frame(parent, bg=COLORS["bg"])
        wrap.grid(row=0, column=1, sticky="nsew")

        tk.Label(wrap, text="Notification History", font=FONTS["h3"], fg=COLORS["text"],
                  bg=COLORS["bg"]).pack(anchor="w", pady=(0, 8))

        filter_wrap = tk.Frame(wrap, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        filter_wrap.pack(fill="x")
        self.history_filter = FilterBar(
            filter_wrap,
            filters=[
                ("priority", "Priority", ["All", "Normal", "Important", "Urgent"]),
                ("status", "Status", ["All", "Active", "Expired", "Draft"]),
            ],
            on_change=lambda _v: self._refresh_history(),
        )
        self.history_filter.pack(fill="x", padx=PADDING["md"], pady=PADDING["md"])

        self.history_holder = tk.Frame(wrap, bg=COLORS["bg"])
        self.history_holder.pack(fill="both", expand=True, pady=(10, 0))

        self._refresh_history()

    def _refresh_history(self):
        for w in self.history_holder.winfo_children():
            w.destroy()

        values = self.history_filter.get_values()
        notifications = notification_service.get_notifications(
            search=values.get("search", ""),
            priority=values.get("priority", "All"),
            status=values.get("status", "All"),
        )

        if not notifications:
            StatePlaceholder(self.history_holder, "No notifications match the selected filters.",
                               kind="empty").pack(fill="both", expand=True)
            return

        columns = [
            ("notification_id", "ID", 70, "w"),
            ("title", "Title", 220, "w"),
            ("audience_detail", "Audience", 140, "w"),
            ("priority", "Priority", 90, "center"),
            ("published_by", "Published By", 100, "w"),
            ("published_date", "Published", 100, "center"),
            ("expiration_date", "Expires", 100, "center"),
            ("status", "Status", 90, "center"),
        ]
        table = DataTable(self.history_holder, columns, height=15)
        table.pack(fill="both", expand=True)
        rows = [dict(notification_id=n.notification_id, title=n.title, audience_detail=n.audience_detail,
                       priority=n.priority.title(), published_by=n.published_by,
                       published_date=format_date_display(n.published_date),
                       expiration_date=format_date_display(n.expiration_date),
                       status=n.status.title(), _raw=n) for n in notifications]
        table.set_rows(rows)
