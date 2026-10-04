"""
Report service — Stage 2 (live backend).

Three report types export real server-generated CSV via ?format=csv:
    GET /reports/students, GET /reports/attendance, GET /reports/gatepasses
The other three (Department Attendance, Notification, System Summary) have
no matching backend report endpoint, so they're composed client-side from
other services and exported as CSV locally (csv/io, stdlib only).
"""

import csv
import io
from dataclasses import dataclass

from api.api_client import api_client, ApiClientError
from services import student_service, attendance_service, notification_service, analytics_service
from utils.helpers import now_str, today_str

REPORT_TYPES = [
    "Student Report",
    "Attendance Report",
    "Department Attendance Report",
    "Gate-Pass Report",
    "Notification Report",
    "System Summary Report",
]

_SERVER_BACKED = {
    "Student Report": "/reports/students",
    "Attendance Report": "/reports/attendance",
    "Gate-Pass Report": "/reports/gatepasses",
}


@dataclass
class ReportResult:
    title: str
    generated_on: str
    columns: list
    rows: list
    row_count: int


def _common_params(department, semester, section, date_from, date_to) -> dict:
    return {
        "department": student_service.code_for_department_name(department) if department != "All" else None,
        "semester": int(semester) if semester != "All" else None,
        "section": section if section != "All" else None,
        "date_from": date_from or None,
        "date_to": date_to or None,
    }


def generate_report(report_type: str, department: str = "All", semester: str = "All",
                     section: str = "All", date_from: str = "", date_to: str = "") -> ReportResult:
    if report_type in _SERVER_BACKED:
        path = _SERVER_BACKED[report_type]
        params = _common_params(department, semester, section, date_from, date_to)
        try:
            rows = api_client.get_all_pages(path, params=params, page_size=500)
        except ApiClientError:
            rows = []
        columns = list(rows[0].keys()) if rows else []
        table_rows = [[r.get(c, "") for c in columns] for r in rows]

    elif report_type == "Department Attendance Report":
        summary = attendance_service.get_attendance_summary()
        depts = [department] if department != "All" else list(summary.department_averages.keys())
        columns = ["Department", "Average Attendance"]
        table_rows = [[d, f"{summary.department_averages.get(d, 0.0)}%"] for d in depts]

    elif report_type == "Notification Report":
        notifications = notification_service.get_notifications()
        columns = ["Notification ID", "Title", "Audience", "Priority", "Status", "Published"]
        table_rows = [[n.notification_id, n.title, n.audience_detail, n.priority, n.status, n.published_date]
                      for n in notifications]

    else:  # System Summary Report
        overview = analytics_service.get_analytics()
        columns = ["Metric", "Value"]
        table_rows = [
            ["Total Students", overview.total_students],
            ["Active Students", overview.active_students],
            ["Inactive Students", overview.inactive_students],
            ["Overall Attendance", f"{overview.overall_attendance}%"],
            ["Students Below Threshold", overview.low_attendance_students],
            ["Total Gate Passes", overview.gatepass_total],
            ["Pending Gate Passes", overview.gatepass_pending],
            ["Notifications Published", overview.notifications_published],
            ["Active Notifications", overview.notifications_active],
        ]

    return ReportResult(
        title=report_type, generated_on=now_str(), columns=columns,
        rows=table_rows, row_count=len(table_rows),
    )


def export_report_csv(report_type: str, department: str = "All", semester: str = "All",
                       section: str = "All", date_from: str = "", date_to: str = "") -> bytes:
    """Returns CSV bytes ready to write to disk. Uses the backend's own CSV
    export for the three report types it supports; builds CSV locally
    (stdlib csv module) for the other three."""
    if report_type in _SERVER_BACKED:
        path = _SERVER_BACKED[report_type]
        params = _common_params(department, semester, section, date_from, date_to)
        params["format"] = "csv"
        return api_client.get_raw(path, params=params)

    result = generate_report(report_type, department, semester, section, date_from, date_to)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(result.columns)
    writer.writerows(result.rows)
    return buffer.getvalue().encode("utf-8")
