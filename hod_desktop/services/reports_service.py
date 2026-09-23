"""
Reports service — Stage 1 generates sample/mock report content in
memory. Stage 2 will call a backend report-generation endpoint and
likely return a file (PDF/CSV) to download instead of in-memory text.

No backend report storage is implemented here, per spec.
"""

from datetime import datetime

from mock import mock_data
from services import attendance_service, analytics_service

REPORT_TYPES = [
    "Department Attendance Report",
    "Student Attendance Report",
    "Gate Pass Report",
    "Notification Report",
]


def generate_report(report_type: str, params: dict | None = None) -> dict:
    """
    Returns a dict with a title, generated-at timestamp, and a list of
    text lines making up the report body — enough for the Reports
    screen to render a readable preview.

    Future API: POST /api/reports/generate (returns a file handle/URL)
    """
    params = params or {}
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if report_type == "Department Attendance Report":
        lines = _department_attendance_report()
    elif report_type == "Student Attendance Report":
        lines = _student_attendance_report(params.get("student_id"))
    elif report_type == "Gate Pass Report":
        lines = _gatepass_report()
    elif report_type == "Notification Report":
        lines = _notification_report()
    else:
        raise ValueError(f"Unknown report type: {report_type}")

    return {"title": report_type, "generated_at": generated_at, "lines": lines}


def _department_attendance_report():
    avg = analytics_service.get_department_average()
    dist = analytics_service.get_attendance_distribution()
    lines = [
        f"Department: {mock_data.DEPARTMENT}",
        f"Overall average attendance: {avg}%",
        f"Total students: {dist['total']}",
        f"  Good (90%+):      {dist['good']}",
        f"  Normal (75-89%):  {dist['normal']}",
        f"  Attention (<75%): {dist['attention']}",
        "",
        "Subject-wise breakdown:",
    ]
    for row in analytics_service.get_subject_wise_attendance():
        lines.append(f"  {row['subject']:<28} {row['percentage']}%")
    return lines


def _student_attendance_report(student_id):
    records = attendance_service.get_department_attendance()
    if student_id:
        records = [r for r in records if r.student_id == student_id]
    if not records:
        return ["No attendance records found for the given student."]
    lines = [f"Attendance detail for {records[0].student_name} ({records[0].student_id})", ""]
    for r in records:
        lines.append(f"  {r.subject:<28} {r.present}/{r.classes_held}  ({r.percentage}%)")
    return lines


def _gatepass_report():
    passes = mock_data.MOCK_GATEPASSES
    pending = sum(1 for p in passes if p["status"] == "PENDING")
    approved = sum(1 for p in passes if p["status"] == "APPROVED")
    rejected = sum(1 for p in passes if p["status"] == "REJECTED")
    lines = [
        f"Total gate-pass requests: {len(passes)}",
        f"  Pending:  {pending}",
        f"  Approved: {approved}",
        f"  Rejected: {rejected}",
        "",
        "Recent decisions:",
    ]
    decided = [p for p in passes if p["decided_at"]]
    decided.sort(key=lambda p: p["decided_at"], reverse=True)
    for p in decided[:8]:
        lines.append(
            f"  [{p['decided_at']}] {p['student_name']} — {p['status']}"
        )
    return lines


def _notification_report():
    notes = mock_data.MOCK_NOTIFICATIONS
    lines = [f"Total notifications published: {len(notes)}", ""]
    for n in notes:
        lines.append(f"  [{n['created_at']}] {n['title']} — {n['audience']} ({n['status']})")
    return lines
