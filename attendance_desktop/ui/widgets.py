import tkinter as tk
from tkinter import ttk
from config.settings import COLORS as C

def setup_style(root):
    st = ttk.Style(root); st.theme_use("clam"); root.configure(bg=C["bg"])
    st.configure("TFrame", background=C["bg"]); st.configure("Card.TFrame", background=C["card"])
    st.configure("TLabel", background=C["bg"], foreground=C["text"], font=("Segoe UI", 10))
    st.configure("Card.TLabel", background=C["card"])
    st.configure("H1.TLabel", font=("Segoe UI", 18, "bold")); st.configure("Muted.TLabel", foreground=C["muted"])
    st.configure("Big.TLabel", background=C["card"], font=("Segoe UI", 24, "bold"), foreground=C["accent"])
    st.configure("TButton", font=("Segoe UI", 10), padding=6)
    st.configure("Accent.TButton", background=C["accent"], foreground="white")
    st.map("Accent.TButton", background=[("active", "#2559c4"), ("disabled", "#a9b8d9")])
    st.configure("Treeview", rowheight=26, font=("Segoe UI", 10)); st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

def card(parent, title, var):
    f = ttk.Frame(parent, style="Card.TFrame", padding=14)
    ttk.Label(f, text=title, style="Card.TLabel").pack(anchor="w")
    ttk.Label(f, textvariable=var, style="Big.TLabel").pack(anchor="w"); return f

def table(parent, cols, widths=None):
    fr = ttk.Frame(parent); tv = ttk.Treeview(fr, columns=cols, show="headings", selectmode="browse")
    sb = ttk.Scrollbar(fr, command=tv.yview); tv.configure(yscrollcommand=sb.set)
    for i, c in enumerate(cols): tv.heading(c, text=c); tv.column(c, width=(widths or {}).get(c, 110), anchor="w")
    tv.tag_configure("PRESENT", foreground=C["ok"]); tv.tag_configure("ABSENT", foreground=C["bad"])
    tv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y"); return fr, tv

def fill(tv, rows, empty="No records to display."):
    tv.delete(*tv.get_children())
    for r, tag in rows: tv.insert("", "end", values=r, tags=(tag,) if tag else ())
    if not rows: tv.insert("", "end", values=(empty,) + ("",) * (len(tv["columns"]) - 1))
