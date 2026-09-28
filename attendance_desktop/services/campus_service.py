"""Service layer used by the UI. UI never touches api/ or qr/ directly."""
import csv, random
from datetime import datetime
from api.api_client import ApiError
from config import settings
from models.models import *
from qr.session_manager import QrSessionManager, QrError

class ServiceError(Exception): ...

class CampusService:
    def __init__(self, api):
        self.api, self.faculty, self.qr, self.current, self.students = api, None, None, None, []

    # ---- auth / lookups
    def authenticate_faculty(self, user: str, pw: str) -> Faculty:
        if not user.strip() or not pw: raise ServiceError("Enter your Faculty ID and password.")
        try: self.faculty = self.api.login(user.strip(), pw)
        except ApiError as e: raise ServiceError(str(e))
        return self.faculty
    def get_subjects(self): return self.api.get_subjects()
    def get_academic_groups(self): return self.api.get_groups()

    # ---- session lifecycle
    def create_and_start_session(self, group, subject, date: str, start: str, minutes: str):
        try:
            datetime.strptime(date, "%Y-%m-%d"); datetime.strptime(start, "%H:%M"); mins = int(minutes)
            if not 1 <= mins <= 180: raise ValueError
        except ValueError:
            raise ServiceError("Invalid session configuration. Check date (YYYY-MM-DD), start (HH:MM) and duration (1-180).")
        if self.current and self.current.status == ACTIVE: raise ServiceError("Close the active session first.")
        n = sum(r.session.date == date and r.session.subject_id == subject.subject_id for r in self.api.list_reports()) + 1
        sid = f"{subject.subject_id[4:]}-{date.replace('-', '')}-{n:03d}"
        self.current = AttendanceSession(sid, self.faculty.faculty_id, group.department_id, group.semester,
                                         group.section, subject.subject_id, subject.name, date, start)
        self.students = self.api.get_students(group)
        self.qr = QrSessionManager(sid, mins * 60, settings.QR_ROTATE_SECONDS)   # FUTURE: POST /api/attendance/sessions
        return self.current

    def qr_payload(self) -> str: return self.qr.token()
    def remaining_seconds(self) -> int: return self.qr.remaining() if self.qr else 0
    def has_active(self) -> bool: return bool(self.current and self.current.status == ACTIVE)

    def live_attendance(self):
        names = {s.student_id: s for s in self.students}
        rows = sorted(self.qr.records.values(), key=lambda r: r.marked_at, reverse=True) if self.qr else []
        return [(r, names[r.student_id]) for r in rows]
    def counts(self):
        p = len(self.qr.records) if self.qr else 0
        return p, len(self.students) - p, len(self.students)

    def simulate_scan(self, bad_token=False, duplicate=False):
        """Demo helper standing in for a student phone scan (students scan via their own app)."""
        pool = [s for s in self.students if s.student_id not in self.qr.records]
        if duplicate and self.qr.records: sid = next(iter(self.qr.records))
        elif pool: sid = random.choice(pool).student_id
        else: return False, "All students are already marked."
        try:
            self.qr.mark(sid, "SC|bogus|0|x" if bad_token else self.qr.token()); return True, f"{sid} marked present."
        except QrError as e: return False, str(e)

    def close_session(self) -> AttendanceReport:
        self.qr.close(); s = self.current
        s.status, s.end_time = CLOSED, datetime.now().strftime("%H:%M")
        recs = [self.qr.records.get(st.student_id) or AttendanceRecord(st.student_id, s.session_id, "ABSENT")
                for st in self.students]
        p = sum(r.status == "PRESENT" for r in recs); t = len(recs)
        rep = AttendanceReport(s, t, p, t - p, round(100 * p / t, 1) if t else 0.0, recs, len(self.qr.rejected))
        self.api.save_report(rep); return rep

    def finalize(self, rep):
        if rep.session.status != CLOSED: raise ServiceError("Only closed sessions can be finalized.")
        rep.session.status = READY

    def submit_attendance_report(self, rep):
        s = rep.session
        if s.status not in (READY, FAILED): raise ServiceError("Finalize attendance before submitting.")
        payload = {"session_id": s.session_id, "faculty_id": s.faculty_id, "department_id": s.department_id,
                   "subject_id": s.subject_id, "semester": s.semester, "section": s.section, "date": s.date,
                   "attendance": [{"student_id": r.student_id, "status": r.status, "marked_at": r.marked_at} for r in rep.records]}
        try: res = self.api.submit_report(payload)
        except ApiError as e: s.status = FAILED; raise ServiceError(str(e))
        s.status, s.submission_id = SUBMITTED, res["submission_id"]
        return res

    def get_history(self): return self.api.list_reports()
    def student_lookup(self, rep):
        s = rep.session
        g = next((g for g in self.get_academic_groups() if (g.department_id, g.semester, g.section) == (s.department_id, s.semester, s.section)), None)
        return {x.student_id: x for x in self.api.get_students(g)} if g else {}

    def export_report_csv(self, rep, path: str):
        try:
            look = self.student_lookup(rep); s = rep.session
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Session", s.session_id, s.subject_name, s.date]); w.writerow([])
                w.writerow(["Student ID", "Name", "Roll No", "Status", "Marked At"])
                for r in rep.records:
                    st = look.get(r.student_id); w.writerow([r.student_id, st.name if st else "", st.roll_no if st else "", r.status, r.marked_at])
        except OSError: raise ServiceError("Report generation failed. Could not write the file.")
