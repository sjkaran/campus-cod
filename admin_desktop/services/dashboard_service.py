"""
Dashboard service.

Stage 1: getDashboardData() -> mock aggregation of other mock modules.
Stage 2: getDashboardData() -> ApiClient -> GET /api/admin/dashboard
"""

from dataclasses import dataclass

from mock.students import get_all_students
from mock.attendance import compute_summary
from mock.gatepasses import get_all_gatepasses
from mock.notifications import get_all_notifications


@dataclass
class DashboardData:
    total_students: int
    active_students: int
    average_attendance: float
    pending_gatepasses: int
    todays_attendance: float
    notifications_published: int
    recent_notifications: list
    recent_gatepasses: list


def get_dashboard_data() -> DashboardData:
    students = get_all_students()
    active_students = [s for s in students if s.is_active]
    summary = compute_summary()
    gatepasses = get_all_gatepasses()
    notifications = get_all_notifications()

    pending = [g for g in gatepasses if g.status == "PENDING"]
    recent_gatepasses = sorted(gatepasses, key=lambda g: g.submitted_date, reverse=True)[:6]
    recent_notifications = [n for n in notifications if n.status == "ACTIVE"][:5]

    # "Today's attendance" is simulated as a small variance around the
    # overall percentage, representative of a daily snapshot vs. term average.
    todays_attendance = round(min(100.0, max(0.0, summary.overall_percentage + 3.1)), 1)

    return DashboardData(
        total_students=len(students),
        active_students=len(active_students),
        average_attendance=summary.overall_percentage,
        pending_gatepasses=len(pending),
        todays_attendance=todays_attendance,
        notifications_published=len(notifications),
        recent_notifications=recent_notifications,
        recent_gatepasses=recent_gatepasses,
    )
