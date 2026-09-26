"""
Mock attendance dataset.

FUTURE API INTEGRATION
Replace this module's data source with:
    GET /api/attendance
    GET /api/attendance/summary
    GET /api/attendance/students/{id}
"""

import random

from config.settings import ATTENDANCE_WARNING_THRESHOLD, ATTENDANCE_CRITICAL_THRESHOLD
from models.attendance import AttendanceRecord, AttendanceSummary
from mock.students import get_all_students
from utils.helpers import today_str, safe_divide

SUBJECTS_BY_DEPARTMENT = {
    "Computer Science": ["Artificial Intelligence", "Data Structures", "Operating Systems", "DBMS", "Computer Networks"],
    "Electronics & Communication": ["Signals & Systems", "Digital Electronics", "VLSI Design", "Communication Systems"],
    "Mechanical Engineering": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "Manufacturing Processes"],
    "Civil Engineering": ["Structural Analysis", "Geotechnical Engineering", "Surveying", "Concrete Technology"],
    "Electrical Engineering": ["Power Systems", "Control Systems", "Electrical Machines", "Circuit Theory"],
}

_ATTENDANCE_CACHE: list[AttendanceRecord] | None = None


def _generate_attendance(seed: int = 7) -> list[AttendanceRecord]:
    rng = random.Random(seed)
    records: list[AttendanceRecord] = []
    students = [s for s in get_all_students() if s.is_active]

    for student in students:
        subjects = SUBJECTS_BY_DEPARTMENT.get(student.department, ["General Studies"])
        # each active student has attendance for 2-3 subjects this term
        chosen = rng.sample(subjects, k=min(len(subjects), rng.randint(2, 3)))
        for subject in chosen:
            classes_held = rng.randint(30, 45)
            # Skew present rate so most students are healthy, some are weak
            base_rate = rng.choices(
                population=[0.95, 0.85, 0.72, 0.58],
                weights=[0.45, 0.30, 0.17, 0.08],
                k=1,
            )[0]
            present = min(classes_held, max(0, round(classes_held * base_rate + rng.uniform(-2, 2))))
            absent = classes_held - present
            records.append(
                AttendanceRecord(
                    student_id=student.student_id,
                    student_name=student.name,
                    department=student.department,
                    semester=student.semester,
                    section=student.section,
                    subject=subject,
                    classes_held=classes_held,
                    present=present,
                    absent=absent,
                    date=today_str(),
                )
            )
    return records


def get_all_attendance() -> list[AttendanceRecord]:
    global _ATTENDANCE_CACHE
    if _ATTENDANCE_CACHE is None:
        _ATTENDANCE_CACHE = _generate_attendance()
    return _ATTENDANCE_CACHE


def get_attendance_for_student(student_id: str) -> list[AttendanceRecord]:
    return [r for r in get_all_attendance() if r.student_id == student_id]


def compute_summary() -> AttendanceSummary:
    records = get_all_attendance()
    if not records:
        return AttendanceSummary(0.0, {}, {}, {}, 0, 0, 0)

    # Overall percentage weighted by classes held
    total_present = sum(r.present for r in records)
    total_held = sum(r.classes_held for r in records)
    overall = round(safe_divide(total_present, total_held) * 100, 1)

    dept_totals: dict[str, list[int]] = {}
    sem_totals: dict[int, list[int]] = {}
    for r in records:
        dept_totals.setdefault(r.department, [0, 0])
        dept_totals[r.department][0] += r.present
        dept_totals[r.department][1] += r.classes_held
        sem_totals.setdefault(r.semester, [0, 0])
        sem_totals[r.semester][0] += r.present
        sem_totals[r.semester][1] += r.classes_held

    department_averages = {
        dept: round(safe_divide(p, h) * 100, 1) for dept, (p, h) in dept_totals.items()
    }
    semester_averages = {
        sem: round(safe_divide(p, h) * 100, 1) for sem, (p, h) in sem_totals.items()
    }

    # Per-student overall percentage, for threshold counts
    per_student: dict[str, list[int]] = {}
    for r in records:
        per_student.setdefault(r.student_id, [0, 0])
        per_student[r.student_id][0] += r.present
        per_student[r.student_id][1] += r.classes_held

    below = 0
    critical = 0
    for _sid, (p, h) in per_student.items():
        pct = safe_divide(p, h) * 100
        if pct < ATTENDANCE_CRITICAL_THRESHOLD:
            critical += 1
            below += 1
        elif pct < ATTENDANCE_WARNING_THRESHOLD:
            below += 1

    return AttendanceSummary(
        overall_percentage=overall,
        department_averages=department_averages,
        semester_averages=semester_averages,
        students_below_threshold=below,
        students_critically_below_threshold=critical,
        total_students_tracked=len(per_student),
    )
