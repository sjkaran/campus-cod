"""Attendance service — API boundary for attendance viewing/filtering."""

from config.settings import DATA_SOURCE_MODE, ATTENDANCE_NORMAL_THRESHOLD
from models.attendance import AttendanceRecord
from mock import mock_data


def _to_attendance_dict(r: dict) -> dict:
    """Map a backend AttendanceSessionSummary to AttendanceRecord fields."""
    return {
        "student_id": r.get("student_id", ""),
        "student_name": r.get("student_name", ""),
        "department": r.get("department_code", r.get("department", "")),
        "semester": r.get("semester", 0),
        "section": r.get("section", ""),
        "subject": r.get("subject_name", r.get("subject_code", r.get("subject", ""))),
        "classes_held": r.get("total_classes", r.get("classes_held", 0)),
        "present": r.get("present", 0),
    }


def get_filter_options() -> dict:
    """Populates filter dropdowns."""
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            depts_data = api_client.get_data("/departments") or []
            classes_data = api_client.get_data("/academic-classes") or []
            departments = [d.get("name", d.get("code", "")) for d in depts_data]
            semesters = sorted({c.get("semester") for c in classes_data if c.get("semester")})
            sections = sorted({c.get("section") for c in classes_data if c.get("section")})
            return {
                "departments": departments or ["All"],
                "semesters": semesters,
                "sections": sections,
                "subjects": [],
            }
        except ApiClientError as e:
            raise RuntimeError(str(e))

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
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        params = {}
        if semester and semester != "All":
            params["semester"] = semester
        if section and section != "All":
            params["section"] = section
        if subject and subject != "All":
            params["subject"] = subject
        try:
            rows = api_client.get_department_attendance(params or None)
            return [AttendanceRecord.from_dict(_to_attendance_dict(r)) for r in rows]
        except ApiClientError as e:
            raise RuntimeError(str(e))

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
    Returns aggregate stats used on the dashboard: overall department
    attendance %, and count of students below the attention threshold.
    """
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
