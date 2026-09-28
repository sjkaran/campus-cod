import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from config import settings
from config.settings import COLORS as C
from models.models import *
from qr.generator import qr_photo
from services.campus_service import ServiceError
from ui.widgets import card, table, fill

class Screen(ttk.Frame):
    def __init__(self, app): super().__init__(app.content, padding=20); self.app, self.svc = app, app.svc
    def on_show(self, **kw): ...
    def title(self, t, sub=""):
        ttk.Label(self, text=t, style="H1.TLabel").pack(anchor="w")
        if sub: ttk.Label(self, text=sub, style="Muted.TLabel").pack(anchor="w", pady=(0, 10))

class Login(ttk.Frame):
    def __init__(self, root, on_login):
        super().__init__(root); self.on_login = on_login
        box = ttk.Frame(self, style="Card.TFrame", padding=30); box.place(relx=.5, rely=.45, anchor="center")
        ttk.Label(box, text="Smart Campus", style="Card.TLabel", font=("Segoe UI", 20, "bold")).pack()
        ttk.Label(box, text="Attendance Faculty Sign-in", style="Card.TLabel").pack(pady=(0, 14))
        self.u, self.p, self.msg = tk.StringVar(value="FAC001"), tk.StringVar(), tk.StringVar()
        ttk.Label(box, text="Faculty ID / Username", style="Card.TLabel").pack(anchor="w")
        ttk.Entry(box, textvariable=self.u, width=32).pack(pady=(0, 8))
        ttk.Label(box, text="Password", style="Card.TLabel").pack(anchor="w")
        self.pw = ttk.Entry(box, textvariable=self.p, show="•", width=32); self.pw.pack()
        self.show = tk.BooleanVar(); ttk.Checkbutton(box, text="Show password", variable=self.show, style="Card.TLabel",
            command=lambda: self.pw.config(show="" if self.show.get() else "•")).pack(anchor="w", pady=6)
        ttk.Label(box, textvariable=self.msg, style="Card.TLabel", foreground=C["bad"]).pack()
        ttk.Button(box, text="Login", style="Accent.TButton", command=self.on_login).pack(fill="x", pady=(6, 0))
        self.pw.bind("<Return>", lambda e: self.on_login())

class Dashboard(Screen):
    def __init__(self, app):
        super().__init__(app); self.v = {k: tk.StringVar(value="–") for k in ("Today's Sessions", "Active Session", "Students Present", "Attendance Submitted")}
        self.hello = tk.StringVar(); self.title("Dashboard"); ttk.Label(self, textvariable=self.hello, style="Muted.TLabel").pack(anchor="w")
        row = ttk.Frame(self); row.pack(fill="x", pady=12)
        for i, (k, v) in enumerate(self.v.items()): card(row, k, v).grid(row=0, column=i, padx=6, sticky="nsew"); row.columnconfigure(i, weight=1)
        ttk.Button(self, text="▶  Start New Session", style="Accent.TButton", command=lambda: app.show("session")).pack(anchor="w", pady=6)
        ttk.Label(self, text="Recent attendance reports", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 4))
        fr, self.tv = table(self, ("Session", "Date", "Subject", "Present", "Status")); fr.pack(fill="both", expand=True)
        self.tv.bind("<Double-1>", lambda e: self._open())
    def on_show(self, **kw):
        hist, today = self.svc.get_history(), datetime.now().strftime("%Y-%m-%d")
        self.hello.set(f"{self.svc.faculty.name} — {datetime.now():%A, %d %B %Y}")
        self.v["Today's Sessions"].set(sum(r.session.date == today for r in hist))
        self.v["Active Session"].set(self.svc.current.subject_name if self.svc.has_active() else "None")
        self.v["Students Present"].set(self.svc.counts()[0] if self.svc.has_active() else "–")
        self.v["Attendance Submitted"].set(sum(r.session.status == SUBMITTED for r in hist))
        self.hist = hist[:8]
        fill(self.tv, [((r.session.session_id, r.session.date, r.session.subject_name, f"{r.present}/{r.total_students}", r.session.status), None) for r in self.hist])
    def _open(self):
        i = self.tv.index(self.tv.selection()[0]) if self.tv.selection() else -1
        if 0 <= i < len(self.hist): self.app.show("report", report=self.hist[i])

class NewSession(Screen):
    def __init__(self, app):
        super().__init__(app); self.title("New Attendance Session", "Configure academic details before starting the QR session.")
        f = ttk.Frame(self, style="Card.TFrame", padding=20); f.pack(anchor="w")
        self.groups, self.subjects = self.svc.get_academic_groups(), self.svc.get_subjects()
        self.grp = tk.StringVar(); self.sub = tk.StringVar()
        self.date, self.start, self.dur = tk.StringVar(value=f"{datetime.now():%Y-%m-%d}"), tk.StringVar(value=f"{datetime.now():%H:%M}"), tk.StringVar(value=str(settings.DEFAULT_SESSION_MINUTES))
        gl = [f"{g.department} — Sem {g.semester} — Section {g.section}" for g in self.groups]
        for r, (lbl, w) in enumerate([("Class", ttk.Combobox(f, textvariable=self.grp, values=gl, state="readonly", width=40)),
            ("Subject", ttk.Combobox(f, textvariable=self.sub, values=[s.name for s in self.subjects], state="readonly", width=40)),
            ("Date (YYYY-MM-DD)", ttk.Entry(f, textvariable=self.date, width=42)), ("Start time (HH:MM)", ttk.Entry(f, textvariable=self.start, width=42)),
            ("QR window (minutes)", ttk.Entry(f, textvariable=self.dur, width=42))]):
            ttk.Label(f, text=lbl, style="Card.TLabel").grid(row=r, column=0, sticky="w", pady=6, padx=(0, 16)); w.grid(row=r, column=1)
        self.gl = gl; self.err = tk.StringVar(); ttk.Label(f, textvariable=self.err, style="Card.TLabel", foreground=C["bad"]).grid(row=5, columnspan=2)
        ttk.Button(f, text="Start Session", style="Accent.TButton", command=self.go).grid(row=6, columnspan=2, sticky="e", pady=(10, 0))
    def go(self):
        if not self.grp.get() or not self.sub.get(): self.err.set("Select a class and subject."); return
        try: self.svc.create_and_start_session(self.groups[self.gl.index(self.grp.get())], next(s for s in self.subjects if s.name == self.sub.get()), self.date.get(), self.start.get(), self.dur.get())
        except ServiceError as e: self.err.set(str(e)); return
        self.err.set(""); self.app.show("live")

class Live(Screen):
    def __init__(self, app):
        super().__init__(app); self.head, self.info, self.msg, self.cnt = (tk.StringVar() for _ in range(4)); self._job = None
        ttk.Label(self, textvariable=self.head, style="H1.TLabel").pack(anchor="w"); ttk.Label(self, textvariable=self.info, style="Muted.TLabel").pack(anchor="w")
        body = ttk.Frame(self); body.pack(fill="both", expand=True, pady=10)
        left = ttk.Frame(body, style="Card.TFrame", padding=14); left.pack(side="left", fill="y", padx=(0, 12))
        self.qr = ttk.Label(left, style="Card.TLabel", wraplength=260); self.qr.pack()
        self.timer = ttk.Label(left, style="Big.TLabel"); self.timer.pack(pady=6)
        ttk.Label(left, textvariable=self.cnt, style="Card.TLabel", font=("Segoe UI", 11, "bold")).pack()
        ttk.Label(left, text="Demo — simulate student scans", style="Card.TLabel", foreground=C["muted"]).pack(pady=(14, 2))
        for t, kw in (("Valid scan", {}), ("Duplicate scan", dict(duplicate=True)), ("Invalid QR", dict(bad_token=True))):
            ttk.Button(left, text=t, command=lambda k=kw: self.scan(**k)).pack(fill="x", pady=1)
        self.close_btn = ttk.Button(left, text="Close Session", style="Accent.TButton", command=self.close); self.close_btn.pack(fill="x", pady=(14, 0))
        right = ttk.Frame(body); right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, textvariable=self.msg).pack(anchor="w")
        fr, self.tv = table(right, ("ID", "Student", "Roll No", "Time", "Status"), {"Student": 170}); fr.pack(fill="both", expand=True)
    def on_show(self, **kw):
        if not self.svc.has_active():
            self.head.set("No active session"); self.info.set("Start a session from “New Session”."); self.timer.config(text=""); self.qr.config(image="", text="")
            self.close_btn.state(["disabled"]); fill(self.tv, []); return
        s = self.svc.current; self.close_btn.state(["!disabled"])
        self.head.set(s.subject_name); self.info.set(f"{s.department_id} — Semester {s.semester} — Section {s.section}   |   Session: {s.session_id}   |   Start: {s.start_time}")
        self.msg.set("Loading attendance…"); self.tick()
    def tick(self):
        if self._job: self.after_cancel(self._job)
        if not self.svc.has_active(): return
        rem = self.svc.remaining_seconds(); tok = self.svc.qr_payload()
        if getattr(self, "_tok", None) != tok:
            self._tok, self._img = tok, qr_photo(tok); self.qr.config(image=self._img or "", text="" if self._img else f"(install qrcode + Pillow)\n{tok}")
        if rem == 0: self.qr.config(image="", text="QR session expired."); self._tok = None; self.msg.set("QR session expired. Close the session to review.")
        self.timer.config(text=f"{rem // 60:02d}:{rem % 60:02d}", foreground=C["bad"] if rem < 60 else C["accent"])
        p, a, t = self.svc.counts(); self.cnt.set(f"Present {p}  ·  Absent {a}  ·  Total {t}")
        rows = self.svc.live_attendance()
        fill(self.tv, [((st.student_id, st.name, st.roll_no, r.marked_at, r.status), "PRESENT") for r, st in rows], "No attendance records have been captured.")
        self._job = self.after(1000, self.tick)
    def scan(self, **kw):
        if not self.svc.has_active(): return
        ok, m = self.svc.simulate_scan(**kw); self.msg.set(("✔ " if ok else "✖ ") + m); self.tick()
    def close(self):
        if not messagebox.askokcancel("Close session", "Stop accepting attendance and generate the report?"): return
        rep = self.svc.close_session(); self.app.show("report", report=rep)

class Report(Screen):
    def __init__(self, app):
        super().__init__(app); self.rep = None; self.h, self.sm, self.st = tk.StringVar(), tk.StringVar(), tk.StringVar()
        ttk.Label(self, textvariable=self.h, style="H1.TLabel").pack(anchor="w"); ttk.Label(self, textvariable=self.sm, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(self, textvariable=self.st, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=6)
        bar = ttk.Frame(self); bar.pack(anchor="w")
        self.b_fin = ttk.Button(bar, text="Finalize Attendance", command=self.fin); self.b_sub = ttk.Button(bar, text="Submit to Smart Campus", style="Accent.TButton", command=self.sub)
        self.b_fin.pack(side="left", padx=(0, 6)); self.b_sub.pack(side="left", padx=(0, 6)); ttk.Button(bar, text="Export CSV", command=self.exp).pack(side="left")
        fr, self.tv = table(self, ("Student ID", "Name", "Roll No", "Status", "Time Marked"), {"Name": 180}); fr.pack(fill="both", expand=True, pady=10)
    def on_show(self, report=None, **kw):
        if report is None:
            done = [r for r in self.svc.get_history()]; report = done[0] if done else None
        self.rep = report
        if not report: self.h.set("No reports yet"); self.sm.set(""); self.st.set(""); fill(self.tv, []); return
        self.refresh()
    def refresh(self):
        r, s = self.rep, self.rep.session; look = self.svc.student_lookup(r)
        self.h.set(f"{s.subject_name} — {s.session_id}")
        self.sm.set(f"Faculty {s.faculty_id} · {s.department_id} Sem {s.semester} Sec {s.section} · {s.date} {s.start_time}–{s.end_time or '…'}\nTotal {r.total_students} · Present {r.present} · Absent {r.absent} · {r.attendance_percentage}% · Rejected scans {r.rejected_scans}")
        self.st.set(f"Status: {s.status}" + (f"   (Submission {s.submission_id})" if s.submission_id else ""))
        self.b_fin.state(["!disabled"] if s.status == CLOSED else ["disabled"]); self.b_sub.state(["!disabled"] if s.status in (READY, FAILED) else ["disabled"])
        fill(self.tv, [((x.student_id, look[x.student_id].name if x.student_id in look else "", look[x.student_id].roll_no if x.student_id in look else "", x.status, x.marked_at or "—"), x.status) for x in r.records])
    def fin(self):
        if not messagebox.askokcancel("Finalize", "Finalize attendance for this session?"): return
        try: self.svc.finalize(self.rep)
        except ServiceError as e: messagebox.showerror("Error", str(e))
        self.refresh()
    def sub(self):
        try: self.svc.submit_attendance_report(self.rep); messagebox.showinfo("Submitted", "Attendance submitted successfully.")
        except ServiceError as e: messagebox.showerror("Submission failed", str(e))
        self.refresh()
    def exp(self):
        p = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{self.rep.session.session_id}.csv")
        if not p: return
        try: self.svc.export_report_csv(self.rep, p); messagebox.showinfo("Exported", "Report saved.")
        except ServiceError as e: messagebox.showerror("Error", str(e))

class History(Screen):
    def __init__(self, app):
        super().__init__(app); self.title("Attendance History"); bar = ttk.Frame(self); bar.pack(anchor="w", pady=6)
        self.q, self.d, self.sub, self.dept, self.stat = (tk.StringVar() for _ in range(5))
        for lbl, v, vals in (("Search", self.q, None), ("Date", self.d, None), ("Subject", self.sub, [""] + [s.name for s in self.svc.get_subjects()]),
                             ("Dept", self.dept, ["", "CSE"]), ("Status", self.stat, ["", ACTIVE, CLOSED, READY, SUBMITTED, FAILED])):
            ttk.Label(bar, text=lbl).pack(side="left", padx=(8, 2)); (ttk.Combobox(bar, textvariable=v, values=vals, width=16, state="readonly") if vals else ttk.Entry(bar, textvariable=v, width=14)).pack(side="left")
            v.trace_add("write", lambda *a: self.render())
        cols = ("Session", "Date", "Subject", "Dept", "Sem", "Sec", "Present", "Absent", "Status")
        fr, self.tv = table(self, cols, {"Session": 160, "Subject": 150, "Status": 160, "Dept": 60, "Sem": 50, "Sec": 50}); fr.pack(fill="both", expand=True)
        self.tv.bind("<Double-1>", lambda e: self.open()); ttk.Label(self, text="Double-click a session to open its report.", style="Muted.TLabel").pack(anchor="w")
    def on_show(self, **kw): self.all = self.svc.get_history(); self.render()
    def render(self):
        q = self.q.get().lower(); self.rows = [r for r in self.all if (not q or q in (r.session.session_id + r.session.subject_name).lower())
            and (not self.d.get() or self.d.get() in r.session.date) and (not self.sub.get() or r.session.subject_name == self.sub.get())
            and (not self.dept.get() or r.session.department_id == self.dept.get()) and (not self.stat.get() or r.session.status == self.stat.get())]
        fill(self.tv, [((r.session.session_id, r.session.date, r.session.subject_name, r.session.department_id, r.session.semester, r.session.section, r.present, r.absent, r.session.status), None) for r in self.rows], "No sessions match the filters.")
    def open(self):
        if self.tv.selection():
            i = self.tv.index(self.tv.selection()[0])
            if i < len(self.rows): self.app.show("report", report=self.rows[i])
