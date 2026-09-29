"""Development seed data.   Run:  python -m app.seed [--reset]

DEVELOPMENT CREDENTIALS ONLY - never use in production.
    admin      / Admin@12345
    hod_cse    / Hod@12345      (Head of CSE)
    hod_ece    / Hod@12345      (Head of ECE)
    fac_cse1   / Faculty@12345  (teaches CSE Sem 6-A)
    fac_cse2   / Faculty@12345  (teaches CSE Sem 6-B)
    fac_ece1   / Faculty@12345  (teaches ECE Sem 6-A)
    s2026001 .. s2026016 / Student@12345   (001-008 CSE 6-A, 009-012 CSE 6-B, 013-016 ECE 6-A)
"""
import random
import sys
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.database import SessionLocal, engine
from app import models as m

YEAR = "2026-27"


def _user(db, username: str, role: m.Role, pw_hash: str) -> m.User:
    u = m.User(username=username, password_hash=pw_hash, role=role, is_active=True)
    db.add(u)
    db.flush()
    return u


def seed(reset: bool = False) -> None:
    if settings.is_production:
        raise SystemExit("Refusing to seed development data in production.")
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  # no-op when Alembic already created the tables

    rng = random.Random(42)  # deterministic attendance pattern
    with SessionLocal() as db:
        if db.execute(select(m.User.id).limit(1)).first():
            raise SystemExit("Database already contains data. Re-run with --reset to wipe and reseed.")

        h_admin, h_hod, h_fac, h_stu = (hash_password(p) for p in ("Admin@12345", "Hod@12345", "Faculty@12345", "Student@12345"))

        depts = {c: m.Department(code=c, name=n) for c, n in
                 [("CSE", "Computer Science & Engineering"), ("ECE", "Electronics & Communication"),
                  ("ME", "Mechanical Engineering"), ("CE", "Civil Engineering")]}
        db.add_all(depts.values())
        db.flush()

        subjects = {}
        for code, name, dept in [
            ("CS601", "Compiler Design", "CSE"), ("CS602", "Computer Networks", "CSE"), ("CS603", "Machine Learning", "CSE"),
            ("EC601", "VLSI Design", "ECE"), ("EC602", "Digital Signal Processing", "ECE"),
            ("ME601", "Heat Transfer", "ME"), ("CE601", "Structural Analysis", "CE"),
        ]:
            subjects[code] = m.Subject(code=code, name=name, department_id=depts[dept].id, credits=4)
        db.add_all(subjects.values())

        classes = {
            "CSE-A": m.AcademicClass(department_id=depts["CSE"].id, semester=6, section="A", academic_year=YEAR),
            "CSE-B": m.AcademicClass(department_id=depts["CSE"].id, semester=6, section="B", academic_year=YEAR),
            "ECE-A": m.AcademicClass(department_id=depts["ECE"].id, semester=6, section="A", academic_year=YEAR),
        }
        db.add_all(classes.values())
        db.flush()

        # --- staff -----------------------------------------------------------
        admin_u = _user(db, "admin", m.Role.ADMIN, h_admin)
        db.add(m.Admin(user_id=admin_u.id, employee_id="ADM001", name="Asha Verma"))

        hods = {}
        for dept, uname, name in [("CSE", "hod_cse", "Dr. R. Mishra"), ("ECE", "hod_ece", "Dr. S. Patnaik")]:
            u = _user(db, uname, m.Role.HOD, h_hod)
            hods[dept] = m.Hod(user_id=u.id, employee_id=f"HOD-{dept}", name=name, department_id=depts[dept].id)
            db.add(hods[dept])

        faculty = {}
        for uname, fid, name, dept, cls_key, subs in [
            ("fac_cse1", "F001", "Prof. Anil Das", "CSE", "CSE-A", ["CS601", "CS602"]),
            ("fac_cse2", "F002", "Prof. Meera Nayak", "CSE", "CSE-B", ["CS603"]),
            ("fac_ece1", "F003", "Prof. Kiran Rout", "ECE", "ECE-A", ["EC601", "EC602"]),
        ]:
            u = _user(db, uname, m.Role.FACULTY, h_fac)
            f = m.Faculty(user_id=u.id, faculty_id=fid, name=name, email=f"{uname}@campus.test", department_id=depts[dept].id)
            db.add(f)
            db.flush()
            for s in subs:
                db.add(m.FacultyAssignment(faculty_id=f.id, subject_id=subjects[s].id, academic_class_id=classes[cls_key].id))
            faculty[uname] = f

        # --- students --------------------------------------------------------
        first = ["Aarav", "Diya", "Kabir", "Ishita", "Rohan", "Sneha", "Vivaan", "Ananya",
                 "Aditya", "Pooja", "Nikhil", "Riya", "Arjun", "Kavya", "Manish", "Tanvi"]
        layout = [("CSE", "A")] * 8 + [("CSE", "B")] * 4 + [("ECE", "A")] * 4
        students = []
        for i, (dept, sec) in enumerate(layout, start=1):
            sid = f"S2026{i:03d}"
            u = _user(db, sid.lower(), m.Role.STUDENT, h_stu)
            s = m.Student(
                user_id=u.id, student_id=sid, roll_number=f"{dept}26{i:03d}", name=f"{first[i-1]} Kumar",
                email=f"{sid.lower()}@campus.test", phone=f"90000{i:05d}", department_id=depts[dept].id,
                semester=6, section=sec,
            )
            db.add(s)
            students.append(s)
        db.flush()

        # --- attendance: submitted sessions for CSE-A (fac_cse1) -------------
        today = date.today()
        cse_a = [s for s in students if s.department_id == depts["CSE"].id and s.section == "A"]
        for n in range(8):
            subj = subjects["CS601" if n % 2 == 0 else "CS602"]
            sess = m.AttendanceSession(
                external_session_id=f"QR-SEED-{n:03d}", faculty_id=faculty["fac_cse1"].id, subject_id=subj.id,
                academic_class_id=classes["CSE-A"].id, date=today - timedelta(days=n + 1),
                start_time=time(9, 0), end_time=time(10, 0), status=m.SessionStatus.SUBMITTED,
                finalized_at=datetime.now(timezone.utc), submitted_at=datetime.now(timezone.utc),
            )
            db.add(sess)
            db.flush()
            for idx, s in enumerate(cse_a):
                # student index 0-1 are chronically absent to give the low-attendance list content
                p_present = 0.35 if idx < 2 else 0.9
                status = m.AttendanceStatus.PRESENT if rng.random() < p_present else m.AttendanceStatus.ABSENT
                db.add(m.AttendanceRecord(session_id=sess.id, student_id=s.id, status=status))

        # An ACTIVE session so the faculty app has something to work with.
        db.add(m.AttendanceSession(
            external_session_id="QR-SEED-LIVE", faculty_id=faculty["fac_cse2"].id, subject_id=subjects["CS603"].id,
            academic_class_id=classes["CSE-B"].id, date=today, status=m.SessionStatus.ACTIVE,
        ))

        # --- gate passes -----------------------------------------------------
        def gp(student, days_ahead, status, remarks=None, hod=None, reason="Family function"):
            dep = today + timedelta(days=days_ahead)
            g = m.GatePass(
                student_id=student.id, destination="Home - Cuttack", reason=reason,
                departure_date=dep, departure_time=time(16, 0), return_date=dep + timedelta(days=2),
                return_time=time(18, 0), status=status, hod_remarks=remarks,
            )
            if hod:
                g.hod_id = hod.id
                g.reviewed_at = datetime.now(timezone.utc)
            db.add(g)

        gp(students[0], 2, m.GatePassStatus.PENDING)
        gp(students[1], 3, m.GatePassStatus.PENDING, reason="Medical appointment")
        gp(students[2], 1, m.GatePassStatus.APPROVED, hod=hods["CSE"], remarks="Approved")
        gp(students[3], 1, m.GatePassStatus.REJECTED, hod=hods["CSE"], remarks="Internal exams that week")
        gp(students[12], 2, m.GatePassStatus.PENDING, reason="Sibling wedding")

        # --- notifications ---------------------------------------------------
        n1 = m.Notification(title="Semester exam schedule released", message="The end-semester timetable is now on the notice board.",
                            created_by=admin_u.id, priority=m.Priority.IMPORTANT, audience_type=m.AudienceType.ALL_STUDENTS)
        n2 = m.Notification(title="CSE: Compiler Design lab moved", message="Lab moves to Lab-3 from Monday.",
                            created_by=hods["CSE"].user_id, priority=m.Priority.NORMAL, audience_type=m.AudienceType.DEPARTMENT,
                            targets=[m.NotificationTarget(department_id=depts["CSE"].id)])
        n3 = m.Notification(title="Campus closed Friday", message="Campus will remain closed on Friday for maintenance.",
                            created_by=admin_u.id, priority=m.Priority.URGENT, audience_type=m.AudienceType.ALL_STUDENTS)
        db.add_all([n1, n2, n3])
        db.commit()
    print("Seed complete. Credentials are listed at the top of app/seed.py (development only).")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
