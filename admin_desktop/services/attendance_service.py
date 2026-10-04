"""
Attendance service — Stage 2 (live backend).

Uses GET /reports/attendance (per-student/subject rows) as the single
source of truth for both the Attendance screen's table and the summary
statistics, so the two can never disagree with each other.
"""

from models.attendance import AttendanceRecord, AttendanceSummary
from api.api_client import api_client, ApiClientError
from services import student_service
from config.settings import ATTENDANCE_WARNING_THRESHOLD, ATTENDANCE_CRITICAL_THRESHOLD
from utils.helpers import safe_divide

_subjects_cache: list[dict] | None = None


def _load_subjects() -> list[dict]:
    global _subjects_cache
    if _subjects_cache is None:
        try:
            _subjects_cache = api_client.get_data("/subjects") or []
        except ApiClientError:
            _subjects_cache = []
    return _subjects_cache


def get_all_subjects() -> list[str]:
    return sorted({s["name"] for s in _load_subjects()})


def _code_for_subject_name(name: str) -> str | None:
    for s in _load_subjects():
        if s["name"] == name:
            return s["code"]
    return None


def _status_for_percentage(pct: float) -> str:
    if pct < ATTENDANCE_CRITICAL_THRESHOLD:
        return "CRITICAL"
    if pct < ATTENDANCE_WARNING_THRESHOLD:
        return "BELOW THRESHOLD"
    return "HEALTHY"


def _fetch_report_rows(department="All", semester="All", section="All", subject="All") -> list[dict]:
    params = {
        "department": student_service.code_for_department_name(department) if department != "All" else None,
        "semester": int(semester) if semester != "All" else None,
        "section": section if section != "All" else None,
        "subject": _code_for_subject_name(subject) if subject != "All" else None,
    }
    try:
        return api_client.get_all_pages("/reports/attendance", params=params, page_size=500)
    except ApiClientError:
        return []


def get_attendance(department: str = "All", semester: str = "All", section: str = "All",
                    subject: str = "All", status: str = "All", search: str = "") -> list[AttendanceRecord]:
    """FUTURE (now live): GET /reports/attendance?department=&semester=&section=&subject="""
    rows = _fetch_report_rows(department, semester, section, subject)
    search = (search or "").strip().lower()

    records = [
        AttendanceRecord(
            student_id=r["student_id"], student_name=r["student_name"],
            department=student_service.name_for_department_code(r["department_code"]),
            semester=r["semester"], section=r["section"],
            subject=r.get("subject_name", r.get("subject_code", "")),
            classes_held=r["total_classes"], present=r["present"], absent=r["absent"], date="",
        )
        for r in rows
    ]

    def matches(rec: AttendanceRecord) -> bool:
        if status != "All" and _status_for_percentage(rec.percentage) != status.upper():
            return False
        if search and search not in f"{rec.student_id} {rec.student_name}".lower():
            return False
        return True

    return [r for r in records if matches(r)]


def get_attendance_summary() -> AttendanceSummary:
    """Built from the full (unfiltered) attendance report, mirroring exactly
    what the Attendance/Analytics screens compute, so every screen agrees."""
    rows = _fetch_report_rows()
    if not rows:
        return AttendanceSummary(0.0, {}, {}, 0, 0, 0)

    total_present = sum(r["present"] for r in rows)
    total_held = sum(r["total_classes"] for r in rows)
    overall = round(safe_divide(total_present, total_held) * 100, 1)

    dept_totals: dict[str, list[int]] = {}
    sem_totals: dict[int, list[int]] = {}
    per_student: dict[str, list[int]] = {}
    for r in rows:
        dept_name = student_service.name_for_department_code(r["department_code"])
        dept_totals.setdefault(dept_name, [0, 0])
        dept_totals[dept_name][0] += r["present"]
        dept_totals[dept_name][1] += r["total_classes"]

        sem_totals.setdefault(r["semester"], [0, 0])
        sem_totals[r["semester"]][0] += r["present"]
        sem_totals[r["semester"]][1] += r["total_classes"]

        per_student.setdefault(r["student_id"], [0, 0])
        per_student[r["student_id"]][0] += r["present"]
        per_student[r["student_id"]][1] += r["total_classes"]

    department_averages = {d: round(safe_divide(p, h) * 100, 1) for d, (p, h) in dept_totals.items()}
    semester_averages = {s: round(safe_divide(p, h) * 100, 1) for s, (p, h) in sem_totals.items()}

    below = critical = 0
    for p, h in per_student.values():
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
