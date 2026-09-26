"""
Report service.

Stage 1: generateReport() -> assembled in-memory from mock datasets.
Stage 2: -> ApiClient -> GET /api/reports/students, /api/reports/attendance,
                         /api/reports/gatepasses (etc.)

A report is returned as a generic (columns, rows) structure so the Reports
UI screen does not need to know the shape of any individual report type.
"""

from dataclasses import dataclass

from mock.students import get_all_students, DEPARTMENTS
from mock.attendance import get_all_attendance, compute_summary
from mock.gatepasses import get_all_gatepasses
from mock.notifications import get_all_notifications
from mock.analytics import get_overview

REPORT_TYPES = [
    "Student Report",
    "Attendance Report",
    "Department Attendance Report",
    "Gate-Pass Report",
    "Notification Report",
    "System Summary Report",
]


@dataclass
class ReportResult:
    title: str
    generated_on: str
    columns: list
    rows: list
    row_count: int


def _filter_common(items, department, semester, section, get_dept, get_sem=None, get_sec=None):
    result = items
    if department and department != "All":
        result = [i for i in result if get_dept(i) == department]
    if semester and semester != "All" and get_sem:
        result = [i for i in result if str(get_sem(i)) == str(semester)]
    if section and section != "All" and get_sec:
        result = [i for i in result if get_sec(i) == section]
    return result


def generate_report(report_type: str, department: str = "All", semester: str = "All",
                     section: str = "All", date_from: str = "", date_to: str = "") -> ReportResult:
    from utils.helpers import now_str

    if report_type == "Student Report":
        students = _filter_common(get_all_students(), department, semester, section,
                                   get_dept=lambda s: s.department, get_sem=lambda s: s.semester,
                                   get_sec=lambda s: s.section)
        columns = ["Student ID", "Name", "Roll No.", "Department", "Sem", "Section", "Status"]
        rows = [[s.student_id, s.name, s.roll_number, s.department, s.semester, s.section, s.status]
                for s in students]

    elif report_type == "Attendance Report":
        records = _filter_common(get_all_attendance(), department, semester, section,
                                  get_dept=lambda r: r.department, get_sem=lambda r: r.semester,
                                  get_sec=lambda r: r.section)
        columns = ["Student ID", "Name", "Subject", "Held", "Present", "Absent", "%"]
        rows = [[r.student_id, r.student_name, r.subject, r.classes_held, r.present, r.absent,
                 f"{r.percentage}%"] for r in records]

    elif report_type == "Department Attendance Report":
        summary = compute_summary()
        columns = ["Department", "Average Attendance"]
        depts = [department] if department != "All" else list(summary.department_averages.keys())
        rows = [[d, f"{summary.department_averages.get(d, 0.0)}%"] for d in depts]

    elif report_type == "Gate-Pass Report":
        records = _filter_common(get_all_gatepasses(), department, "All", "All",
                                  get_dept=lambda g: g.department)
        if date_from:
            records = [g for g in records if g.submitted_date >= date_from]
        if date_to:
            records = [g for g in records if g.submitted_date <= date_to]
        columns = ["Request ID", "Student", "Department", "Destination", "Status", "Submitted"]
        rows = [[g.request_id, g.student_name, g.department, g.destination, g.status, g.submitted_date]
                for g in records]

    elif report_type == "Notification Report":
        notifications = get_all_notifications()
        columns = ["Notification ID", "Title", "Audience", "Priority", "Status", "Published"]
        rows = [[n.notification_id, n.title, n.audience_detail, n.priority, n.status, n.published_date]
                for n in notifications]

    else:  # System Summary Report
        overview = get_overview()
        columns = ["Metric", "Value"]
        rows = [
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
        title=report_type,
        generated_on=now_str(),
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )
