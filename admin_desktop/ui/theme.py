"""Central ttk style configuration — keeps visual language consistent and
avoids inline style tweaks scattered across screens."""

from tkinter import ttk

from config.settings import COLORS, FONTS


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=COLORS["bg"])

    # Buttons -----------------------------------------------------------
    style.configure("Primary.TButton", background=COLORS["primary"], foreground=COLORS["primary_text"],
                     font=FONTS["body_bold"], padding=(14, 8), borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_hover"]), ("disabled", COLORS["border"])])

    style.configure("Secondary.TButton", background=COLORS["surface"], foreground=COLORS["text"],
                     font=FONTS["body"], padding=(14, 8), borderwidth=1, relief="solid")
    style.map("Secondary.TButton", background=[("active", COLORS["surface_alt"])])

    style.configure("Danger.TButton", background=COLORS["danger"], foreground="#FFFFFF",
                     font=FONTS["body_bold"], padding=(14, 8), borderwidth=0)
    style.map("Danger.TButton", background=[("active", "#B91C1C")])

    style.configure("Link.TButton", background=COLORS["surface"], foreground=COLORS["primary"],
                     font=FONTS["small_bold"], borderwidth=0)

    # Sidebar nav buttons -------------------------------------------------
    style.configure("Sidebar.TButton", background=COLORS["sidebar_bg"], foreground=COLORS["sidebar_text"],
                     font=FONTS["sidebar"], borderwidth=0, anchor="w", padding=(18, 10))
    style.map("Sidebar.TButton",
              background=[("active", COLORS["sidebar_bg_active"])],
              foreground=[("active", COLORS["sidebar_text_active"])])

    style.configure("SidebarActive.TButton", background=COLORS["sidebar_bg_active"],
                     foreground=COLORS["sidebar_text_active"], font=FONTS["body_bold"],
                     borderwidth=0, anchor="w", padding=(18, 10))
    style.map("SidebarActive.TButton", background=[("active", COLORS["sidebar_bg_active"])])

    # Entries / combos ------------------------------------------------
    style.configure("Admin.TEntry", fieldbackground=COLORS["surface"], foreground=COLORS["text"],
                     bordercolor=COLORS["border"], lightcolor=COLORS["border"], darkcolor=COLORS["border"],
                     padding=6)
    style.configure("Admin.TCombobox", fieldbackground=COLORS["surface"], foreground=COLORS["text"],
                     padding=5)

    # Treeview ----------------------------------------------------------
    style.configure("Admin.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                     foreground=COLORS["text"], rowheight=28, font=FONTS["body"], borderwidth=0)
    style.configure("Admin.Treeview.Heading", background=COLORS["neutral_bg"], foreground=COLORS["neutral_text"],
                     font=FONTS["small_bold"], relief="flat", padding=(8, 8))
    style.map("Admin.Treeview.Heading", background=[("active", COLORS["border"])])
    style.map("Admin.Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", COLORS["text"])])

    # Notebook (tabs), if used ------------------------------------------
    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=COLORS["surface_alt"], foreground=COLORS["text_muted"],
                     font=FONTS["body_bold"], padding=(16, 8))
    style.map("TNotebook.Tab", background=[("selected", COLORS["surface"])],
              foreground=[("selected", COLORS["primary"])])

    # Scrollbars ----------------------------------------------------------
    style.configure("Vertical.TScrollbar", background=COLORS["surface_alt"], troughcolor=COLORS["bg"],
                     bordercolor=COLORS["bg"], arrowcolor=COLORS["text_muted"])
    style.configure("Horizontal.TScrollbar", background=COLORS["surface_alt"], troughcolor=COLORS["bg"],
                     bordercolor=COLORS["bg"], arrowcolor=COLORS["text_muted"])

    return style
