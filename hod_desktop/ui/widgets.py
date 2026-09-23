"""Reusable composite widgets shared across HOD screens."""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts


class Card(ttk.Frame):
    """A white rounded-feel panel with consistent padding/border."""

    def __init__(self, parent, padding=(18, 16), **kwargs):
        super().__init__(parent, style="Card.TFrame", padding=padding, **kwargs)
        self._add_border()

    def _add_border(self):
        self.configure(borderwidth=1, relief="solid")


class StatCard(Card):
    """Dashboard summary card: big number, label, optional tone."""

    TONE_COLORS = {
        "default": Colors.PRIMARY,
        "success": Colors.SUCCESS,
        "warning": Colors.WARNING,
        "danger": Colors.DANGER,
    }

    def __init__(self, parent, label, value, tone="default", **kwargs):
        super().__init__(parent, **kwargs)
        color = self.TONE_COLORS.get(tone, Colors.PRIMARY)

        value_lbl = tk.Label(
            self, text=str(value), font=Fonts.STAT, fg=color, bg=Colors.CARD_BG,
        )
        value_lbl.pack(anchor="w")

        label_lbl = ttk.Label(self, text=label, style="CardMuted.TLabel")
        label_lbl.pack(anchor="w", pady=(4, 0))

        self.value_lbl = value_lbl

    def set_value(self, value):
        self.value_lbl.configure(text=str(value))


class StatusBadge(tk.Label):
    """Small colored pill showing PENDING / APPROVED / REJECTED."""

    STYLES = {
        "PENDING": (Colors.PENDING_BG, Colors.PENDING, "Pending"),
        "APPROVED": (Colors.SUCCESS_BG, Colors.SUCCESS, "Approved"),
        "REJECTED": (Colors.DANGER_BG, Colors.DANGER, "Rejected"),
        "PUBLISHED": (Colors.SUCCESS_BG, Colors.SUCCESS, "Published"),
        "EXPIRED": (Colors.BORDER, Colors.TEXT_MUTED, "Expired"),
        "good": (Colors.SUCCESS_BG, Colors.ATTN_GOOD, "Good"),
        "normal": (Colors.WARNING_BG, Colors.ATTN_NORMAL, "Normal"),
        "attention": (Colors.DANGER_BG, Colors.ATTN_LOW, "Attention"),
    }

    def __init__(self, parent, status, **kwargs):
        bg, fg, text = self.STYLES.get(status, (Colors.BORDER, Colors.TEXT_SECONDARY, status))
        super().__init__(
            parent, text=f"  {text}  ", bg=bg, fg=fg,
            font=Fonts.SMALL_BOLD, padx=2, pady=3, **kwargs
        )


class EmptyState(ttk.Frame):
    """Shown when a table/list has no data."""

    def __init__(self, parent, message="Nothing to show here yet.", icon="—", **kwargs):
        super().__init__(parent, style="App.TFrame", **kwargs)
        tk.Label(self, text=icon, font=(Fonts.FAMILY, 28), bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(pady=(30, 6))
        ttk.Label(self, text=message, style="Muted.TLabel").pack()


class SectionHeader(ttk.Frame):
    """Page title + optional subtitle + optional right-side action slot."""

    def __init__(self, parent, title, subtitle=None, **kwargs):
        super().__init__(parent, style="App.TFrame", **kwargs)
        left = ttk.Frame(self, style="App.TFrame")
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text=title, style="H1.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(left, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))
        self.action_slot = ttk.Frame(self, style="App.TFrame")
        self.action_slot.pack(side="right")


class ScrollableFrame(ttk.Frame):
    """A vertically scrollable container — used for long forms/lists."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="App.TFrame", **kwargs)
        canvas = tk.Canvas(self, bg=Colors.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas, style="App.TFrame")

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            delta = -1 * (event.delta // 120) if event.delta else 0
            canvas.yview_scroll(delta, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)


def make_table(parent, columns, height=12):
    """
    Builds a ttk.Treeview with consistent styling and a vertical
    scrollbar, returned alongside its containing frame.
    columns: list of (key, heading, width, anchor) tuples.
    """
    container = ttk.Frame(parent, style="App.TFrame")
    tree = ttk.Treeview(
        container, columns=[c[0] for c in columns], show="headings",
        style="App.Treeview", height=height,
    )
    for key, heading, width, anchor in columns:
        tree.heading(key, text=heading)
        tree.column(key, width=width, anchor=anchor, stretch=True)

    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return container, tree


def confirm_dialog(parent, title, message) -> bool:
    from tkinter import messagebox
    return messagebox.askyesno(title, message, parent=parent)


def info_dialog(parent, title, message):
    from tkinter import messagebox
    messagebox.showinfo(title, message, parent=parent)


def error_dialog(parent, title, message):
    from tkinter import messagebox
    messagebox.showerror(title, message, parent=parent)
