"""
Reusable UI components shared across all Admin screens.

Centralizing these avoids repeated UI code and keeps a single professional
visual language across the application (tables, cards, badges, dialogs,
loading/empty/error states, and lightweight canvas-based charts).
"""

import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS, PADDING


# ---------------------------------------------------------------------------
# Status badge
# ---------------------------------------------------------------------------
_STATUS_STYLE = {
    "ACTIVE": ("success", "success_bg"),
    "APPROVED": ("success", "success_bg"),
    "HEALTHY": ("success", "success_bg"),
    "PENDING": ("warning", "warning_bg"),
    "DRAFT": ("warning", "warning_bg"),
    "BELOW THRESHOLD": ("warning", "warning_bg"),
    "INACTIVE": ("danger", "danger_bg"),
    "REJECTED": ("danger", "danger_bg"),
    "EXPIRED": ("danger", "danger_bg"),
    "CRITICAL": ("danger", "danger_bg"),
    "NORMAL": ("info", "info_bg"),
    "IMPORTANT": ("warning", "warning_bg"),
    "URGENT": ("danger", "danger_bg"),
}


def status_badge(parent, text: str) -> tk.Label:
    key = (text or "").upper().replace("_", " ")
    fg_key, bg_key = _STATUS_STYLE.get(key, ("neutral_text", "neutral_bg"))
    lbl = tk.Label(
        parent, text=text.replace("_", " ").title() if text else "—",
        font=FONTS["small_bold"], fg=COLORS[fg_key], bg=COLORS[bg_key],
        padx=10, pady=2,
    )
    return lbl


# ---------------------------------------------------------------------------
# KPI Card
# ---------------------------------------------------------------------------
class KPICard(tk.Frame):
    def __init__(self, parent, label: str, value: str, accent: str = "primary",
                 subtitle: str = "", **kwargs):
        super().__init__(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, **kwargs)
        bar = tk.Frame(self, bg=COLORS.get(accent, COLORS["primary"]), width=4)
        bar.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=COLORS["surface"])
        inner.pack(side="left", fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["md"])

        tk.Label(inner, text=label, font=FONTS["small_bold"], fg=COLORS["text_muted"],
                  bg=COLORS["surface"]).pack(anchor="w")
        self.value_label = tk.Label(inner, text=value, font=FONTS["kpi_value"],
                                      fg=COLORS["text"], bg=COLORS["surface"])
        self.value_label.pack(anchor="w", pady=(2, 0))
        if subtitle:
            tk.Label(inner, text=subtitle, font=FONTS["small"], fg=COLORS["text_subtle"],
                      bg=COLORS["surface"]).pack(anchor="w")

    def set_value(self, value: str):
        self.value_label.config(text=value)


# ---------------------------------------------------------------------------
# Section / card container
# ---------------------------------------------------------------------------
class Card(tk.Frame):
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"],
                          highlightthickness=1, **kwargs)
        if title:
            header = tk.Frame(self, bg=COLORS["surface"])
            header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["md"], 0))
            tk.Label(header, text=title, font=FONTS["h3"], fg=COLORS["text"],
                      bg=COLORS["surface"]).pack(anchor="w")
        self.body = tk.Frame(self, bg=COLORS["surface"])
        self.body.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["md"])


# ---------------------------------------------------------------------------
# State placeholders: loading / empty / error
# ---------------------------------------------------------------------------
class StatePlaceholder(tk.Frame):
    def __init__(self, parent, message: str, kind: str = "empty", on_retry=None, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)
        icon = {"loading": "⏳", "empty": "🗂", "error": "⚠"}.get(kind, "•")
        color = COLORS["danger"] if kind == "error" else COLORS["text_muted"]
        wrap = tk.Frame(self, bg=COLORS["surface"])
        wrap.place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(wrap, text=icon, font=(FONTS["h1"][0], 26), fg=color,
                  bg=COLORS["surface"]).pack()
        tk.Label(wrap, text=message, font=FONTS["body"], fg=color,
                  bg=COLORS["surface"]).pack(pady=(6, 0))
        if kind == "error" and on_retry:
            ttk.Button(wrap, text="Try Again", command=on_retry, style="Primary.TButton").pack(pady=(10, 0))


# ---------------------------------------------------------------------------
# Confirmation dialog
# ---------------------------------------------------------------------------
def confirm_dialog(parent, title: str, message: str, confirm_text: str = "Confirm",
                    danger: bool = False) -> bool:
    result = {"confirmed": False}
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.configure(bg=COLORS["surface"])
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    frame = tk.Frame(dialog, bg=COLORS["surface"], padx=24, pady=20)
    frame.pack()

    tk.Label(frame, text=title, font=FONTS["h3"], fg=COLORS["text"],
              bg=COLORS["surface"]).pack(anchor="w")
    tk.Label(frame, text=message, font=FONTS["body"], fg=COLORS["text_muted"],
              bg=COLORS["surface"], wraplength=340, justify="left").pack(anchor="w", pady=(10, 20))

    btn_row = tk.Frame(frame, bg=COLORS["surface"])
    btn_row.pack(anchor="e")

    def on_cancel():
        result["confirmed"] = False
        dialog.destroy()

    def on_confirm():
        result["confirmed"] = True
        dialog.destroy()

    ttk.Button(btn_row, text="Cancel", command=on_cancel, style="Secondary.TButton").pack(side="left", padx=(0, 8))
    style_name = "Danger.TButton" if danger else "Primary.TButton"
    ttk.Button(btn_row, text=confirm_text, command=on_confirm, style=style_name).pack(side="left")

    dialog.update_idletasks()
    # Center relative to parent
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    dw, dh = dialog.winfo_width(), dialog.winfo_height()
    dialog.geometry(f"+{px + (pw - dw) // 2}+{py + (ph - dh) // 2}")

    parent.wait_window(dialog)
    return result["confirmed"]


def info_dialog(parent, title: str, message: str):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.configure(bg=COLORS["surface"])
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    frame = tk.Frame(dialog, bg=COLORS["surface"], padx=24, pady=20)
    frame.pack()
    tk.Label(frame, text=f"✓  {title}", font=FONTS["h3"], fg=COLORS["success"],
              bg=COLORS["surface"]).pack(anchor="w")
    tk.Label(frame, text=message, font=FONTS["body"], fg=COLORS["text_muted"],
              bg=COLORS["surface"], wraplength=340, justify="left").pack(anchor="w", pady=(10, 20))
    ttk.Button(frame, text="OK", command=dialog.destroy, style="Primary.TButton").pack(anchor="e")

    dialog.update_idletasks()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    dw, dh = dialog.winfo_width(), dialog.winfo_height()
    dialog.geometry(f"+{px + (pw - dw) // 2}+{py + (ph - dh) // 2}")


# ---------------------------------------------------------------------------
# Data table (Treeview wrapper) with optional status-column badge rendering
# ---------------------------------------------------------------------------
class DataTable(tk.Frame):
    """A styled, sortable, scrollable Treeview table.

    columns: list of (key, heading, width, anchor)
    on_select: callback(row_dict) fired on double-click / Enter
    """

    def __init__(self, parent, columns, on_row_activate=None, height=16, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)
        self.columns = columns
        self.on_row_activate = on_row_activate
        self._rows_by_iid = {}
        self._sort_state = {}

        tree_frame = tk.Frame(self, bg=COLORS["surface"])
        tree_frame.pack(fill="both", expand=True)

        col_keys = [c[0] for c in columns]
        self.tree = ttk.Treeview(tree_frame, columns=col_keys, show="headings",
                                   height=height, style="Admin.Treeview")
        for key, heading, width, anchor in columns:
            self.tree.heading(key, text=heading, command=lambda k=key: self._sort_by(k))
            self.tree.column(key, width=width, anchor=anchor, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("oddrow", background=COLORS["surface_alt"])
        self.tree.tag_configure("evenrow", background=COLORS["surface"])

        if on_row_activate:
            self.tree.bind("<Double-1>", self._handle_activate)
            self.tree.bind("<Return>", self._handle_activate)

        self._all_rows = []

    def _handle_activate(self, _event):
        selection = self.tree.selection()
        if selection and self.on_row_activate:
            row = self._rows_by_iid.get(selection[0])
            if row:
                self.on_row_activate(row)

    def set_rows(self, rows: list[dict]):
        """rows: list of dicts keyed by column key, plus '_raw' original object."""
        self._all_rows = rows
        self.tree.delete(*self.tree.get_children())
        self._rows_by_iid.clear()
        for i, row in enumerate(rows):
            values = [row.get(key, "") for key, *_ in self.columns]
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self._rows_by_iid[iid] = row

    def _sort_by(self, key):
        ascending = self._sort_state.get(key, True)
        try:
            rows_sorted = sorted(self._all_rows, key=lambda r: (r.get(key) is None, r.get(key)),
                                   reverse=not ascending)
        except TypeError:
            rows_sorted = sorted(self._all_rows, key=lambda r: str(r.get(key, "")), reverse=not ascending)
        self._sort_state[key] = not ascending
        self.set_rows(rows_sorted)

    def get_selected_row(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self._rows_by_iid.get(selection[0])


# ---------------------------------------------------------------------------
# Filter bar: a horizontal row of search + dropdown filters + clear button
# ---------------------------------------------------------------------------
class FilterBar(tk.Frame):
    def __init__(self, parent, filters: list[tuple], on_change=None, show_search=True, **kwargs):
        """filters: list of (key, label, options_list)"""
        super().__init__(parent, bg=COLORS["surface"], **kwargs)
        self.on_change = on_change
        self.vars = {}

        col = 0
        if show_search:
            tk.Label(self, text="Search", font=FONTS["small_bold"], fg=COLORS["text_muted"],
                      bg=COLORS["surface"]).grid(row=0, column=col, sticky="w", padx=(0, 4))
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(self, textvariable=self.search_var, width=24, style="Admin.TEntry")
            search_entry.grid(row=1, column=col, sticky="w", padx=(0, 16))
            self.search_var.trace_add("write", lambda *_: self._fire())
            col += 1
        else:
            self.search_var = None

        for key, label, options in filters:
            tk.Label(self, text=label, font=FONTS["small_bold"], fg=COLORS["text_muted"],
                      bg=COLORS["surface"]).grid(row=0, column=col, sticky="w", padx=(0, 4))
            var = tk.StringVar(value=options[0])
            combo = ttk.Combobox(self, textvariable=var, values=options, state="readonly",
                                   width=16, style="Admin.TCombobox")
            combo.grid(row=1, column=col, sticky="w", padx=(0, 16))
            combo.bind("<<ComboboxSelected>>", lambda *_: self._fire())
            self.vars[key] = var
            col += 1

        clear_btn = ttk.Button(self, text="Clear Filters", command=self._clear, style="Secondary.TButton")
        clear_btn.grid(row=1, column=col, sticky="w")

    def _fire(self):
        if self.on_change:
            self.on_change(self.get_values())

    def _clear(self):
        if self.search_var is not None:
            self.search_var.set("")
        for var in self.vars.values():
            # Reset to first option; comboboxes retain their own options list
            pass
        for key, var in self.vars.items():
            pass
        self._fire()

    def get_values(self) -> dict:
        values = {"search": self.search_var.get() if self.search_var is not None else ""}
        for key, var in self.vars.items():
            values[key] = var.get()
        return values


# ---------------------------------------------------------------------------
# Lightweight canvas-based charts (no external plotting dependency)
# ---------------------------------------------------------------------------
_CHART_PALETTE = ["#2563EB", "#059669", "#D97706", "#DC2626", "#7C3AED", "#0891B2", "#DB2777"]


class BarChart(tk.Canvas):
    def __init__(self, parent, data: dict, width=380, height=220, max_value=None,
                 value_fmt=lambda v: str(v), **kwargs):
        super().__init__(parent, width=width, height=height, bg=COLORS["surface"],
                          highlightthickness=0, **kwargs)
        self._draw(data, width, height, max_value, value_fmt)

    def _draw(self, data, width, height, max_value, value_fmt):
        if not data:
            self.create_text(width // 2, height // 2, text="No data available",
                               fill=COLORS["text_muted"], font=FONTS["small"])
            return
        margin_left, margin_bottom, margin_top = 40, 34, 14
        chart_h = height - margin_bottom - margin_top
        chart_w = width - margin_left - 16
        max_val = max_value or max(data.values()) or 1
        n = len(data)
        gap = 14
        bar_w = max(18, (chart_w - gap * (n - 1)) / n) if n else 20

        # baseline
        self.create_line(margin_left, height - margin_bottom, width - 8, height - margin_bottom,
                           fill=COLORS["border"])

        x = margin_left
        for i, (label, value) in enumerate(data.items()):
            bar_h = (value / max_val) * chart_h if max_val else 0
            color = _CHART_PALETTE[i % len(_CHART_PALETTE)]
            y0 = height - margin_bottom - bar_h
            self.create_rectangle(x, y0, x + bar_w, height - margin_bottom, fill=color, outline="")
            self.create_text(x + bar_w / 2, y0 - 10, text=value_fmt(value), font=FONTS["small_bold"],
                               fill=COLORS["text"])
            label_text = str(label)
            if len(label_text) > 10:
                label_text = label_text[:9] + "…"
            self.create_text(x + bar_w / 2, height - margin_bottom + 14, text=label_text,
                               font=FONTS["small"], fill=COLORS["text_muted"])
            x += bar_w + gap


class DonutChart(tk.Canvas):
    def __init__(self, parent, data: dict, width=220, height=220, **kwargs):
        super().__init__(parent, width=width, height=height, bg=COLORS["surface"],
                          highlightthickness=0, **kwargs)
        self._draw(data, width, height)

    def _draw(self, data, width, height):
        total = sum(data.values())
        if not total:
            self.create_text(width // 2, height // 2, text="No data available",
                               fill=COLORS["text_muted"], font=FONTS["small"])
            return
        size = min(width, height) - 20
        x0, y0 = (width - size) / 2, (height - size) / 2
        x1, y1 = x0 + size, y0 + size
        start = 90
        for i, (label, value) in enumerate(data.items()):
            extent = -(value / total) * 360
            color = _CHART_PALETTE[i % len(_CHART_PALETTE)]
            self.create_arc(x0, y0, x1, y1, start=start, extent=extent, fill=color, outline=COLORS["surface"], width=2)
            start += extent
        # inner hole for donut effect
        hole = size * 0.55
        hx0, hy0 = (width - hole) / 2, (height - hole) / 2
        self.create_oval(hx0, hy0, hx0 + hole, hy0 + hole, fill=COLORS["surface"], outline="")
        self.create_text(width / 2, height / 2, text=str(total), font=FONTS["h3"], fill=COLORS["text"])


class LegendList(tk.Frame):
    def __init__(self, parent, data: dict, value_fmt=lambda v: str(v), **kwargs):
        super().__init__(parent, bg=COLORS["surface"], **kwargs)
        for i, (label, value) in enumerate(data.items()):
            color = _CHART_PALETTE[i % len(_CHART_PALETTE)]
            row = tk.Frame(self, bg=COLORS["surface"])
            row.pack(fill="x", pady=2)
            tk.Canvas(row, width=10, height=10, bg=COLORS["surface"], highlightthickness=0).pack(side="left")
            swatch = tk.Frame(row, width=10, height=10, bg=color)
            swatch.place(in_=row, x=0, y=2)
            tk.Label(row, text=f"  {label}", font=FONTS["small"], fg=COLORS["text"],
                      bg=COLORS["surface"]).pack(side="left")
            tk.Label(row, text=value_fmt(value), font=FONTS["small_bold"], fg=COLORS["text_muted"],
                      bg=COLORS["surface"]).pack(side="right")
