import tkinter as tk
from tkinter import ttk, messagebox
from config import settings
from config.settings import COLORS as C
from services.campus_service import ServiceError
from ui.widgets import setup_style
from ui import screens as S

class App(tk.Tk):
    def __init__(self, svc):
        super().__init__(); self.svc = svc; self.title(settings.APP_NAME); self.geometry("1180x720"); self.minsize(980, 620)
        setup_style(self); self.shell = None
        self.login = S.Login(self, self.do_login); self.login.pack(fill="both", expand=True)
    def do_login(self):
        try: self.svc.authenticate_faculty(self.login.u.get(), self.login.p.get())
        except ServiceError as e: self.login.msg.set(str(e)); return
        self.login.pack_forget(); self.build_shell()
    def build_shell(self):
        self.shell = ttk.Frame(self); self.shell.pack(fill="both", expand=True)
        top = tk.Frame(self.shell, bg=C["accent"], height=44); top.pack(fill="x")
        tk.Label(top, text=settings.APP_NAME, bg=C["accent"], fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(top, text=f"Faculty: {self.svc.faculty.name}", bg=C["accent"], fg="white").pack(side="right", padx=14)
        side = tk.Frame(self.shell, bg=C["side"], width=190); side.pack(side="left", fill="y"); side.pack_propagate(False)
        self.content = ttk.Frame(self.shell); self.content.pack(side="left", fill="both", expand=True)
        self.screens = {k: cls(self) for k, cls in (("dashboard", S.Dashboard), ("session", S.NewSession), ("live", S.Live), ("report", S.Report), ("history", S.History))}
        for key, label in (("dashboard", "Dashboard"), ("session", "New Session"), ("live", "Live Attendance"), ("report", "Reports"), ("history", "History")):
            tk.Button(side, text=label, anchor="w", bg=C["side"], fg=C["side_fg"], activebackground=C["accent"], activeforeground="white", relief="flat",
                      padx=16, pady=10, command=lambda k=key: self.show(k)).pack(fill="x", pady=1)
        tk.Button(side, text="Logout", anchor="w", bg=C["side"], fg=C["side_fg"], relief="flat", padx=16, pady=10, command=self.logout).pack(side="bottom", fill="x", pady=8)
        self.show("dashboard")
    def show(self, key, **kw):
        for s in self.screens.values(): s.pack_forget()
        self.screens[key].pack(fill="both", expand=True); self.screens[key].on_show(**kw)
    def logout(self):
        if self.svc.has_active() and not messagebox.askokcancel("Logout", "An attendance session is still active. Log out anyway?"): return
        self.shell.destroy(); self.svc.faculty = None; self.login.p.set(""); self.login.pack(fill="both", expand=True)
