"""
Reports service — Stage 2 calls backend report endpoints and formats
the response rows for the UI preview. Mock path remains for offline use.
"""

from datetime import datetime

from config.settings import DATA_SOURCE_MODE

REPORT_TYPES = [
    "Department Attendance Report",
    "Student Attendance Report",
    "Gate Pass Report",
    "Notification Report",
]


def generate_report(report_type: str, params: dict | None = None) -> dict:
    """
    Returns a dict with a title, generated-at timestamp, and a list of
    text lines making up the report body.
    """
    params = params or {}
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if DATA_SOURCE_MODE == "api":
        lines = _api_report(report_type, params)
    else:
        lines = _mock_report(report_type, params)

    return {"title": report_type, "generated_at": generated_at, "lines": lines}


# ------------------------------------------------------------------
# API path
# ------------------------------------------------------------------

def _api_report(report_type: str, params: dict) -> list[str]:
    from api.api_client import api_client, ApiClientError

    if report_type == "Department Attendance Report":
        try:
            rows = api_client.get_all_pages("/reports/attendance", params=params or None)
            return _format_attendance_rows(rows)
        except ApiClientError as e:
            raise RuntimeError(str(e))

    if report_type == "Student Attendance Report":
        student_id = params.get("student_id")
        query = {"student_id": student_id} if student_id else None
        try:
            rows = api_client.get_all_pages("/reports/attendance", params=query)
            if student_id:
                rows = [r for r in rows if r.get("student_id") == student_id]
            return _format_attendance_rows(rows)
        except ApiClientError as e:
            raise RuntimeError(str(e))

    if report_type == "Gate Pass Report":
        try:
            rows = api_client.get_all_pages("/reports/gatepasses", params=None)
            return _format_gatepass_rows(rows)
        except ApiClientError as e:
            raise RuntimeError(str(e))

    if report_type == "Notification Report":
        # No dedicated notifications report endpoint; fall back to listing
        try:
            rows = api_client.get_all_pages("/notifications/created-by-me")
            return _format_notification_rows(rows)
        except ApiClientError as e:
            raise RuntimeError(str(e))

    raise ValueError(f"Unknown report type: {report_type}")


def _format_attendance_rows(rows: list[dict]) -> list[str]:
    if not rows:
        return ["No attendance records found."]
    lines = [
        f"{'Student':<20} {'Subject':<28} {'Present/Total':<16} {'%':>6}",
        "-" * 72,
    ]
    for r in rows:
        total = r.get("total_classes", r.get("classes_held", 0))
        present = r.get("present", 0)
        pct = r.get("percentage", round(present / total * 100, 1) if total else 0.0)
        name = r.get("student_name", r.get("student_id", ""))
        subject = r.get("subject_name", r.get("subject_code", r.get("subject", "")))
        lines.append(f"{name:<20} {subject:<28} {present}/{total:<15} {pct:>5}%")
    return lines


def _format_gatepass_rows(rows: list[dict]) -> list[str]:
    statuses = {"PENDING": 0, "APPROVED": 0, "REJECTED": 0}
    for r in rows:
        s = r.get("status", "PENDING")
        statuses[s] = statuses.get(s, 0) + 1

    lines = [
        f"Total gate-pass requests: {len(rows)}",
        f"  Pending:  {statuses.get('PENDING', 0)}",
        f"  Approved: {statuses.get('APPROVED', 0)}",
        f"  Rejected: {statuses.get('REJECTED', 0)}",
        "",
        "Recent decisions:",
    ]
    decided = [r for r in rows if r.get("reviewed_at") or r.get("decided_at")]
    decided.sort(key=lambda r: r.get("reviewed_at") or r.get("decided_at", ""), reverse=True)
    for r in decided[:8]:
        ts = (r.get("reviewed_at") or r.get("decided_at", ""))[:16]
        name = r.get("student_name", r.get("student_id", ""))
        status = r.get("status", "")
        lines.append(f"  [{ts}] {name} — {status}")
    return lines


def _format_notification_rows(rows: list[dict]) -> list[str]:
    lines = [f"Total notifications published: {len(rows)}", ""]
    for n in rows:
        created = str(n.get("created_at", ""))[:16]
        title = n.get("title", "")
        audience = n.get("audience_type", n.get("audience", ""))
        status = n.get("status", "")
        lines.append(f"  [{created}] {title} — {audience} ({status})")
    return lines


# ------------------------------------------------------------------
# Mock path (in-memory, preserved from Stage 1)
# ------------------------------------------------------------------

def _mock_report(report_type: str, params: dict) -> list[str]:
    from services import attendance_service, analytics_service
    from mock import mock_data

    if report_type == "Department Attendance Report":
        return _mock_dept_attendance(analytics_service, mock_data)
    if report_type == "Student Attendance Report":
        return _mock_student_attendance(attendance_service, params.get("student_id"))
    if report_type == "Gate Pass Report":
        return _mock_gatepass(mock_data)
    if report_type == "Notification Report":
        return _mock_notifications(mock_data)
    raise ValueError(f"Unknown report type: {report_type}")


def _mock_dept_attendance(analytics_service, mock_data):
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


def _mock_student_attendance(attendance_service, student_id):
    records = attendance_service.get_department_attendance()
    if student_id:
        records = [r for r in records if r.student_id == student_id]
    if not records:
        return ["No attendance records found for the given student."]
    lines = [f"Attendance detail for {records[0].student_name} ({records[0].student_id})", ""]
    for r in records:
        lines.append(f"  {r.subject:<28} {r.present}/{r.classes_held}  ({r.percentage}%)")
    return lines


def _mock_gatepass(mock_data):
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
        lines.append(f"  [{p['decided_at']}] {p['student_name']} — {p['status']}")
    return lines


def _mock_notifications(mock_data):
    notes = mock_data.MOCK_NOTIFICATIONS
    lines = [f"Total notifications published: {len(notes)}", ""]
    for n in notes:
        lines.append(f"  [{n['created_at']}] {n['title']} — {n['audience']} ({n['status']})")
    return lines
