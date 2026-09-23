"""Attendance service — API boundary for attendance viewing/filtering."""

from models.attendance import AttendanceRecord
from mock import mock_data


def get_filter_options() -> dict:
    """Populates filter dropdowns. Future API: GET /api/attendance/filters"""
    subjects = sorted({r["subject"] for r in mock_data.MOCK_ATTENDANCE})
    return {
        "departments": [mock_data.DEPARTMENT],
        "semesters": sorted({r["semester"] for r in mock_data.MOCK_ATTENDANCE}),
        "sections": sorted({r["section"] for r in mock_data.MOCK_ATTENDANCE}),
        "subjects": subjects,
    }


def get_department_attendance(
    department: str | None = None,
    semester: int | None = None,
    section: str | None = None,
    subject: str | None = None,
) -> list[AttendanceRecord]:
    """
    Future API: GET /api/attendance/department?dept=&sem=&section=&subject=

    All filter params are optional; None/"" means "no filter" for that field.
    """
    records = []
    for r in mock_data.MOCK_ATTENDANCE:
        if department and department != "All" and r["department"] != department:
            continue
        if semester and semester != "All" and r["semester"] != int(semester):
            continue
        if section and section != "All" and r["section"] != section:
            continue
        if subject and subject != "All" and r["subject"] != subject:
            continue
        records.append(AttendanceRecord.from_dict(r))
    return records


def get_department_summary() -> dict:
    """
    Future API: GET /api/attendance/summary

    Returns aggregate stats used on the dashboard: overall department
    attendance %, and count of students below the attention threshold
    (using the lowest per-student average across subjects).
    """
    from config.settings import ATTENDANCE_NORMAL_THRESHOLD

    all_records = get_department_attendance()
    if not all_records:
        return {"average": 0.0, "below_threshold": 0}

    total_present = sum(r.present for r in all_records)
    total_held = sum(r.classes_held for r in all_records)
    average = round((total_present / total_held) * 100, 1) if total_held else 0.0

    per_student = {}
    for r in all_records:
        per_student.setdefault(r.student_id, []).append(r.percentage)

    below = sum(
        1 for pcts in per_student.values()
        if (sum(pcts) / len(pcts)) < ATTENDANCE_NORMAL_THRESHOLD
    )

    return {"average": average, "below_threshold": below}
