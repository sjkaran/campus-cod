"""
Centralized ttk styling so every screen looks consistent without each
UI module redefining fonts/colors/padding itself.
"""

import tkinter as tk
from tkinter import ttk

from config.settings import Colors, Fonts


def apply_theme(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=Colors.BG)

    style.configure(".", font=Fonts.BODY, background=Colors.BG, foreground=Colors.TEXT_PRIMARY)

    # Frames
    style.configure("App.TFrame", background=Colors.BG)
    style.configure("Card.TFrame", background=Colors.CARD_BG, relief="flat")
    style.configure("Header.TFrame", background=Colors.HEADER_BG)
    style.configure("Sidebar.TFrame", background=Colors.SIDEBAR_BG)

    # Labels
    style.configure("App.TLabel", background=Colors.BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.BODY)
    style.configure("Card.TLabel", background=Colors.CARD_BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.BODY)
    style.configure("CardMuted.TLabel", background=Colors.CARD_BG, foreground=Colors.TEXT_SECONDARY, font=Fonts.SMALL)
    style.configure("Header.TLabel", background=Colors.HEADER_BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.H2)
    style.configure("HeaderSub.TLabel", background=Colors.HEADER_BG, foreground=Colors.TEXT_SECONDARY, font=Fonts.SMALL)
    style.configure("Sidebar.TLabel", background=Colors.SIDEBAR_BG, foreground=Colors.SIDEBAR_TEXT, font=Fonts.BODY)
    style.configure("SidebarBrand.TLabel", background=Colors.SIDEBAR_BG, foreground="#FFFFFF", font=Fonts.H2)
    style.configure("H1.TLabel", background=Colors.BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.H1)
    style.configure("H2.TLabel", background=Colors.BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.H2)
    style.configure("H2Card.TLabel", background=Colors.CARD_BG, foreground=Colors.TEXT_PRIMARY, font=Fonts.H2)
    style.configure("Stat.TLabel", background=Colors.CARD_BG, foreground=Colors.PRIMARY, font=Fonts.STAT)
    style.configure("Muted.TLabel", background=Colors.BG, foreground=Colors.TEXT_MUTED, font=Fonts.SMALL)

    # Status pill-ish labels (rendered as colored labels; true pills via tk.Label backgrounds)
    style.configure("StatusPending.TLabel", background=Colors.PENDING_BG, foreground=Colors.PENDING, font=Fonts.SMALL_BOLD, padding=(8, 2))
    style.configure("StatusApproved.TLabel", background=Colors.SUCCESS_BG, foreground=Colors.SUCCESS, font=Fonts.SMALL_BOLD, padding=(8, 2))
    style.configure("StatusRejected.TLabel", background=Colors.DANGER_BG, foreground=Colors.DANGER, font=Fonts.SMALL_BOLD, padding=(8, 2))

    # Buttons
    style.configure(
        "Primary.TButton",
        background=Colors.PRIMARY, foreground="#FFFFFF",
        font=Fonts.BODY_BOLD, padding=(14, 8), borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", Colors.PRIMARY_DARK), ("disabled", "#9FB3CC")])

    style.configure(
        "Success.TButton",
        background=Colors.SUCCESS, foreground="#FFFFFF",
        font=Fonts.BODY_BOLD, padding=(14, 8), borderwidth=0,
    )
    style.map("Success.TButton", background=[("active", "#167A56"), ("disabled", "#9FCFB9")])

    style.configure(
        "Danger.TButton",
        background=Colors.DANGER, foreground="#FFFFFF",
        font=Fonts.BODY_BOLD, padding=(14, 8), borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", "#9E2E2E"), ("disabled", "#E5AEAE")])

    style.configure(
        "Secondary.TButton",
        background=Colors.CARD_BG, foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY, padding=(14, 8), borderwidth=1,
    )
    style.map("Secondary.TButton", background=[("active", Colors.BG)])

    style.configure(
        "Nav.TButton",
        background=Colors.SIDEBAR_BG, foreground=Colors.SIDEBAR_TEXT,
        font=Fonts.BODY, padding=(16, 10), borderwidth=0, anchor="w",
    )
    style.map(
        "Nav.TButton",
        background=[("active", Colors.SIDEBAR_BG_ACTIVE)],
        foreground=[("active", Colors.SIDEBAR_TEXT_ACTIVE)],
    )
    style.configure(
        "NavActive.TButton",
        background=Colors.SIDEBAR_BG_ACTIVE, foreground=Colors.SIDEBAR_TEXT_ACTIVE,
        font=Fonts.BODY_BOLD, padding=(16, 10), borderwidth=0, anchor="w",
    )
    style.map("NavActive.TButton", background=[("active", Colors.SIDEBAR_BG_ACTIVE)])

    # Entries / Combobox
    style.configure("App.TEntry", padding=6, fieldbackground="#FFFFFF")
    style.configure("App.TCombobox", padding=6, fieldbackground="#FFFFFF")

    # Treeview (tables)
    style.configure(
        "App.Treeview",
        background="#FFFFFF", fieldbackground="#FFFFFF",
        foreground=Colors.TEXT_PRIMARY, rowheight=30, font=Fonts.BODY,
        borderwidth=0,
    )
    style.configure(
        "App.Treeview.Heading",
        background="#EEF1F6", foreground=Colors.TEXT_SECONDARY,
        font=Fonts.SMALL_BOLD, borderwidth=0, padding=(6, 8),
    )
    style.map("App.Treeview", background=[("selected", "#DCE8FA")], foreground=[("selected", Colors.TEXT_PRIMARY)])
    style.layout("App.Treeview", style.layout("Treeview"))

    style.configure("App.TNotebook", background=Colors.BG, borderwidth=0)
    style.configure("App.TNotebook.Tab", font=Fonts.BODY_BOLD, padding=(14, 8))

    style.configure("App.TCheckbutton", background=Colors.CARD_BG, font=Fonts.BODY)
    style.configure("App.TRadiobutton", background=Colors.CARD_BG, font=Fonts.BODY)

    style.configure("App.Horizontal.TSeparator", background=Colors.BORDER)

    return style
