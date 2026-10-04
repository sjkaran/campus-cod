"""
Dashboard service — Stage 2 (live backend).

Composed from the lighter-weight endpoints (not full analytics) since the
dashboard only needs headline numbers plus a handful of recent items:
    GET /students, GET /analytics/attendance, GET /analytics/gatepasses,
    GET /gatepasses, GET /notifications/admin
"""

from dataclasses import dataclass

from api.api_client import api_client, ApiClientError
from services import student_service, gatepass_service, notification_service


@dataclass
class DashboardData:
    total_students: int
    active_students: int
    average_attendance: float
    pending_gatepasses: int
    low_attendance_students: int
    notifications_published: int
    recent_notifications: list
    recent_gatepasses: list


def get_dashboard_data() -> DashboardData:
    try:
        students_resp = api_client.get("/students", params={"page_size": 1})
        total_students = (students_resp.get("pagination") or {}).get("total", 0)
    except ApiClientError:
        total_students = 0
    try:
        active_resp = api_client.get_all_pages("/students", page_size=200)
        active_students = len([s for s in active_resp if s.get("status") == "ACTIVE"])
    except ApiClientError:
        active_students = 0

    try:
        overall = api_client.get_data("/analytics/attendance") or {}
        average_attendance = overall.get("overall", {}).get("percentage", 0.0)
        low_attendance_students = len(overall.get("low_attendance", []))
    except ApiClientError:
        average_attendance = 0.0
        low_attendance_students = 0

    try:
        gp_stats = api_client.get_data("/analytics/gatepasses") or {}
        pending_gatepasses = gp_stats.get("pending", 0)
    except ApiClientError:
        pending_gatepasses = 0

    recent_gatepasses = gatepass_service.get_gatepasses()[:6]
    recent_notifications = [n for n in notification_service.get_notifications() if n.status == "ACTIVE"][:5]

    try:
        notif_resp = api_client.get("/notifications/admin", params={"page_size": 1})
        notifications_published = (notif_resp.get("pagination") or {}).get("total", 0)
    except ApiClientError:
        notifications_published = 0

    return DashboardData(
        total_students=total_students,
        active_students=active_students,
        average_attendance=average_attendance,
        pending_gatepasses=pending_gatepasses,
        low_attendance_students=low_attendance_students,
        notifications_published=notifications_published,
        recent_notifications=recent_notifications,
        recent_gatepasses=recent_gatepasses,
    )
