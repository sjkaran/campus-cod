"""Isolated mock campus data. Replaced by API responses in Stage 2."""
import random
from models.models import *

FACULTY = {"FAC001": ("faculty123", Faculty("FAC001", "Dr. Anita Mishra", "Computer Science"))}
SUBJECTS = [Subject("SUB-AI", "Artificial Intelligence", "CS601", "CSE"),
            Subject("SUB-DBMS", "Database Systems", "CS602", "CSE"),
            Subject("SUB-CN", "Computer Networks", "CS603", "CSE")]
GROUPS = [AcademicGroup("CSE", "Computer Science", 6, "A"), AcademicGroup("CSE", "Computer Science", 6, "B"),
          AcademicGroup("CSE", "Computer Science", 4, "A")]
_NAMES = ["Rahul Sharma", "Priya Singh", "Aman Kumar", "Sneha Patel", "Rohit Das", "Ananya Nayak",
          "Vikram Rao", "Neha Gupta", "Arjun Mehta", "Pooja Reddy", "Karan Joshi", "Isha Verma",
          "Suresh Behera", "Meera Iyer", "Dev Malhotra", "Tanvi Shah", "Nitin Panda", "Kavya Menon",
          "Sahil Khan", "Riya Sen", "Manoj Pradhan", "Diya Kapoor", "Harsh Vora", "Lakshmi Nair"]

def students_for(group: AcademicGroup):
    return [Student(f"ST-{group.department_id}-{i+1:03d}", n, f"{group.semester}{group.section}{i+1:02d}")
            for i, n in enumerate(_NAMES)]

def seed_history(faculty_id: str):
    rnd, out = random.Random(7), []
    for i, (d, sub) in enumerate([("2026-09-24", SUBJECTS[0]), ("2026-09-25", SUBJECTS[1]),
                                  ("2026-09-26", SUBJECTS[2]), ("2026-09-27", SUBJECTS[0])]):
        g = GROUPS[0]; sts = students_for(g)
        s = AttendanceSession(f"{sub.subject_id[4:]}-{d.replace('-','')}-001", faculty_id, g.department_id,
                              g.semester, g.section, sub.subject_id, sub.name, d, "09:00", "09:50",
                              SUBMITTED if i < 3 else READY, f"ATT-SUB-{i+1:03d}" if i < 3 else None)
        recs = [AttendanceRecord(st.student_id, s.session_id, "PRESENT" if rnd.random() > .2 else "ABSENT",
                                 "09:0%d:1%d" % (rnd.randint(1, 8), rnd.randint(0, 9))) for st in sts]
        for r in recs:
            if r.status == "ABSENT": r.marked_at = ""
        p = sum(r.status == "PRESENT" for r in recs)
        out.append(AttendanceReport(s, len(recs), p, len(recs) - p, round(100 * p / len(recs), 1), recs))
    return out
