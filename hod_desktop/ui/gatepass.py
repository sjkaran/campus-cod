"""Screen 3 — Gate Pass Management. The most important HOD feature."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts
from services import gatepass_service
from ui.widgets import (
    Card, StatusBadge, EmptyState, SectionHeader, make_table,
    confirm_dialog, error_dialog, info_dialog,
)


class GatePassScreen(ttk.Frame):
    """
    Two sub-views living in the same screen: the pending-requests table
    (list view) and a detail view for a single selected request. Switching
    between them just swaps which inner frame is packed/gridded.
    """

    def __init__(self, parent, hod_profile):
        super().__init__(parent, style="App.TFrame")
        self.hod_profile = hod_profile
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.list_view = ttk.Frame(self, style="App.TFrame")
        self.detail_view = ttk.Frame(self, style="App.TFrame")
        self.list_view.grid(row=0, column=0, sticky="nsew")
        self.detail_view.grid(row=0, column=0, sticky="nsew")

        self._show_filter = "PENDING"
        self._build_list_view()
        self._show_list()

    # ------------------------------------------------------------------
    # LIST VIEW
    # ------------------------------------------------------------------
    def _build_list_view(self):
        frame = self.list_view
        for child in frame.winfo_children():
            child.destroy()

        header = SectionHeader(frame, "Gate Pass Management",
                                "Review, approve, or reject student gate-pass requests")
        header.pack(fill="x")

        filter_row = ttk.Frame(header.action_slot, style="App.TFrame")
        filter_row.pack()
        self.filter_var = tk.StringVar(value=self._show_filter)
        for value, label in [("PENDING", "Pending"), ("ALL", "All Requests")]:
            rb = ttk.Radiobutton(
                filter_row, text=label, value=value, variable=self.filter_var,
                style="App.TRadiobutton", command=self._refresh_table,
            )
            rb.pack(side="left", padx=6)

        table_card = Card(frame, padding=(0, 0))
        table_card.pack(fill="both", expand=True, pady=(16, 0))
        table_card.configure(borderwidth=1, relief="solid")

        self.table_holder = ttk.Frame(table_card, style="Card.TFrame")
        self.table_holder.pack(fill="both", expand=True, padx=16, pady=16)

        self._refresh_table()

    def _refresh_table(self):
        for child in self.table_holder.winfo_children():
            child.destroy()

        self._show_filter = self.filter_var.get()
        if self._show_filter == "PENDING":
            requests = gatepass_service.get_pending_gatepasses()
        else:
            requests = gatepass_service.get_all_gatepasses()

        if not requests:
            EmptyState(self.table_holder, "No gate-pass requests to show.", icon="🎫").pack(fill="both", expand=True)
            return

        columns = [
            ("id", "Request ID", 90, "w"),
            ("student_id", "Student ID", 90, "w"),
            ("name", "Student Name", 140, "w"),
            ("dept", "Department", 130, "w"),
            ("destination", "Destination", 150, "w"),
            ("departure", "Departure", 130, "center"),
            ("return", "Expected Return", 110, "center"),
            ("status", "Status", 100, "center"),
        ]
        container, tree = make_table(self.table_holder, columns, height=14)
        container.pack(fill="both", expand=True)

        self._row_lookup = {}
        for req in requests:
            row_id = tree.insert("", "end", values=(
                req.request_id, req.student_id, req.student_name, req.department,
                req.destination, f"{req.departure_date} {req.departure_time}",
                req.expected_return, req.status,
            ))
            self._row_lookup[row_id] = req.request_id

        tree.bind("<Double-1>", lambda e: self._open_selected(tree))

        actions = ttk.Frame(self.table_holder, style="Card.TFrame")
        actions.pack(fill="x", pady=(10, 0))
        ttk.Label(actions, text="Double-click a row, or select and click View.",
                  style="CardMuted.TLabel").pack(side="left")
        ttk.Button(actions, text="View Selected", style="Secondary.TButton",
                   command=lambda: self._open_selected(tree)).pack(side="right")

    def _open_selected(self, tree):
        selection = tree.selection()
        if not selection:
            error_dialog(self, "No request selected", "Please select a gate-pass request first.")
            return
        request_id = self._row_lookup[selection[0]]
        self._show_detail(request_id)

    def _show_list(self):
        self.list_view.tkraise()

    # ------------------------------------------------------------------
    # DETAIL VIEW
    # ------------------------------------------------------------------
    def _show_detail(self, request_id):
        request = gatepass_service.get_gatepass_details(request_id)
        if request is None:
            error_dialog(self, "Not found", "That gate-pass request could not be found.")
            return

        frame = self.detail_view
        for child in frame.winfo_children():
            child.destroy()

        top = ttk.Frame(frame, style="App.TFrame")
        top.pack(fill="x")
        back_btn = ttk.Button(top, text="← Back to list", style="Secondary.TButton",
                               command=self._back_to_list)
        back_btn.pack(anchor="w")

        ttk.Label(top, text=f"Gate Pass {request.request_id}", style="H1.TLabel").pack(anchor="w", pady=(12, 2))
        StatusBadge(top, request.status).pack(anchor="w")

        body = ttk.Frame(frame, style="App.TFrame")
        body.pack(fill="both", expand=True, pady=(16, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        # Left: student + gate-pass info
        info_card = Card(body)
        info_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(info_card, text="Student Information", style="H2Card.TLabel").pack(anchor="w")
        self._info_row(info_card, "Student Name", request.student_name)
        self._info_row(info_card, "Student ID", request.student_id)
        self._info_row(info_card, "Department", request.department)

        ttk.Separator(info_card, style="App.Horizontal.TSeparator").pack(fill="x", pady=14)

        ttk.Label(info_card, text="Gate Pass Information", style="H2Card.TLabel").pack(anchor="w")
        self._info_row(info_card, "Destination", request.destination)
        self._info_row(info_card, "Reason", request.reason)
        self._info_row(info_card, "Departure", f"{request.departure_date}  at  {request.departure_time}")
        self._info_row(info_card, "Expected Return", request.expected_return)

        if request.status == "REJECTED" and request.rejection_reason:
            ttk.Separator(info_card, style="App.Horizontal.TSeparator").pack(fill="x", pady=14)
            ttk.Label(info_card, text="Rejection Reason", style="H2Card.TLabel").pack(anchor="w")
            tk.Label(info_card, text=request.rejection_reason, bg=Colors.CARD_BG, fg=Colors.DANGER,
                     font=Fonts.BODY, wraplength=420, justify="left").pack(anchor="w", pady=(4, 0))

        if request.status != "PENDING" and request.decided_by:
            ttk.Separator(info_card, style="App.Horizontal.TSeparator").pack(fill="x", pady=14)
            ttk.Label(info_card, text=f"Decision by {request.decided_by} on {request.decided_at}",
                      style="CardMuted.TLabel").pack(anchor="w")

        # Right: history + actions
        right_col = ttk.Frame(body, style="App.TFrame")
        right_col.grid(row=0, column=1, sticky="nsew")

        history_card = Card(right_col)
        history_card.pack(fill="x")
        ttk.Label(history_card, text="Previous Relevant Information", style="H2Card.TLabel").pack(anchor="w")
        tk.Label(history_card, text=request.previous_pass_note, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, font=Fonts.BODY, wraplength=280, justify="left").pack(
            anchor="w", pady=(6, 0)
        )

        if request.status == "PENDING":
            action_card = Card(right_col)
            action_card.pack(fill="x", pady=(14, 0))
            ttk.Label(action_card, text="Decision", style="H2Card.TLabel").pack(anchor="w", pady=(0, 10))

            approve_btn = ttk.Button(
                action_card, text="✓  Approve", style="Success.TButton",
                command=lambda: self._approve(request),
            )
            approve_btn.pack(fill="x", pady=(0, 8))

            reject_btn = ttk.Button(
                action_card, text="✕  Reject", style="Danger.TButton",
                command=lambda: self._open_reject_dialog(request),
            )
            reject_btn.pack(fill="x")

        self.detail_view.tkraise()

    def _info_row(self, parent, label, value):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED, font=Fonts.SMALL, width=16, anchor="w").pack(side="left")
        tk.Label(row, text=value, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, font=Fonts.BODY, anchor="w",
                 wraplength=280, justify="left").pack(side="left", fill="x", expand=True)

    def _back_to_list(self):
        self._refresh_table()
        self._show_list()

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def _approve(self, request):
        if not confirm_dialog(
            self, "Approve Gate Pass",
            f"Approve gate pass for {request.student_name} ({request.student_id})\n"
            f"to {request.destination} on {request.departure_date}?",
        ):
            return
        gatepass_service.approve_gatepass(request.request_id, self.hod_profile["name"])
        info_dialog(self, "Approved", f"Gate pass {request.request_id} has been approved.")
        self._back_to_list()

    def _open_reject_dialog(self, request):
        RejectDialog(self, request, on_confirm=self._reject)

    def _reject(self, request, reason):
        gatepass_service.reject_gatepass(request.request_id, reason, self.hod_profile["name"])
        info_dialog(self, "Rejected", f"Gate pass {request.request_id} has been rejected.")
        self._back_to_list()


class RejectDialog(tk.Toplevel):
    """Modal requiring a non-empty rejection reason."""

    def __init__(self, parent, request, on_confirm):
        super().__init__(parent)
        self.title("Reject Gate Pass")
        self.configure(bg=Colors.CARD_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.request = request
        self.on_confirm = on_confirm

        pad = ttk.Frame(self, style="Card.TFrame", padding=20)
        pad.pack(fill="both", expand=True)

        ttk.Label(pad, text=f"Reject gate pass for {request.student_name}",
                  style="H2Card.TLabel").pack(anchor="w")
        ttk.Label(pad, text="A rejection reason is required and will be visible to the student.",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(2, 12))

        self.text = tk.Text(pad, width=44, height=5, font=Fonts.BODY, wrap="word",
                             relief="solid", borderwidth=1)
        self.text.pack()
        self.text.focus_set()

        self.error_lbl = tk.Label(pad, text="", fg=Colors.DANGER, bg=Colors.CARD_BG, font=Fonts.SMALL)
        self.error_lbl.pack(anchor="w", pady=(6, 0))

        btn_row = ttk.Frame(pad, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(16, 0))
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_row, text="Confirm Rejection", style="Danger.TButton",
                   command=self._submit).pack(side="right")

        self.update_idletasks()
        self._center_on_parent(parent)

    def _center_on_parent(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _submit(self):
        reason = self.text.get("1.0", "end").strip()
        if not reason:
            self.error_lbl.configure(text="Rejection reason cannot be empty.")
            return
        self.destroy()
        self.on_confirm(self.request, reason)
