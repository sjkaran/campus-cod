"""
Analytics service — Stage 2 (live backend).

Composes AnalyticsOverview from several backend endpoints, since there is
no single "overview" resource:
    GET /students (+pagination totals, for department/semester counts)
    GET /analytics/attendance
    GET /analytics/attendance/departments
    GET /analytics/attendance/subjects
    GET /analytics/gatepasses
    GET /notifications/admin (+pagination total)
"""

from collections import Counter

from models.analytics import AnalyticsOverview
from api.api_client import api_client, ApiClientError
from services import student_service, attendance_service


def get_analytics() -> AnalyticsOverview:
    try:
        all_students = student_service.get_students()
    except ApiClientError:
        all_students = []
    students_by_department = dict(Counter(s.department for s in all_students))
    students_by_semester = dict(Counter(s.semester for s in all_students))
    active = len([s for s in all_students if s.status == "ACTIVE"])
    inactive = len(all_students) - active

    try:
        overall_resp = api_client.get_data("/analytics/attendance") or {}
    except ApiClientError:
        overall_resp = {}
    overall_attendance = overall_resp.get("overall", {}).get("percentage", 0.0)
    low_attendance_students = len(overall_resp.get("low_attendance", []))

    try:
        dept_rows = api_client.get_data("/analytics/attendance/departments") or []
    except ApiClientError:
        dept_rows = []
    attendance_by_department = {row["label"]: row["summary"]["percentage"] for row in dept_rows}

    try:
        subject_rows = api_client.get_data("/analytics/attendance/subjects") or []
    except ApiClientError:
        subject_rows = []
    attendance_by_subject = {row["label"]: row["summary"]["percentage"] for row in subject_rows}

    # Semester breakdown has no dedicated endpoint — derived from the same
    # attendance-report aggregation the Attendance screen uses, so it agrees.
    summary = attendance_service.get_attendance_summary()
    attendance_by_semester = summary.semester_averages

    try:
        gp = api_client.get_data("/analytics/gatepasses") or {}
    except ApiClientError:
        gp = {}

    try:
        notif_resp = api_client.get("/notifications/admin", params={"page_size": 100})
        notif_rows = notif_resp.get("data", [])
        notifications_total = (notif_resp.get("pagination") or {}).get("total", len(notif_rows))
    except ApiClientError:
        notif_rows, notifications_total = [], 0
    notifications_active = len([n for n in notif_rows if n.get("status") == "ACTIVE"])
    notifications_by_audience = dict(Counter(n["audience_type"] for n in notif_rows))

    return AnalyticsOverview(
        total_students=len(all_students),
        students_by_department=students_by_department,
        students_by_semester=students_by_semester,
        active_students=active,
        inactive_students=inactive,
        overall_attendance=overall_attendance,
        attendance_by_department=attendance_by_department,
        attendance_by_semester=attendance_by_semester,
        attendance_by_subject=attendance_by_subject,
        low_attendance_students=low_attendance_students,
        gatepass_total=gp.get("total", 0),
        gatepass_pending=gp.get("pending", 0),
        gatepass_approved=gp.get("approved", 0),
        gatepass_rejected=gp.get("rejected", 0),
        notifications_published=notifications_total,
        notifications_active=notifications_active,
        notifications_by_audience=notifications_by_audience,
    )
