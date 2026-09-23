"""
Dashboard service — pulls a small summary from the other services so
ui/dashboard.py has a single call to make instead of orchestrating
four separate service imports itself.
"""

from services import gatepass_service, attendance_service
from mock import mock_data


def get_dashboard_summary() -> dict:
    """Future API: GET /api/hod/dashboard"""
    pending = gatepass_service.get_pending_gatepasses()
    today_count = gatepass_service.get_today_count()
    att_summary = attendance_service.get_department_summary()
    recent_notifications = mock_data.MOCK_NOTIFICATIONS[:3]

    return {
        "pending_passes": len(pending),
        "today_passes": today_count,
        "department_attendance": att_summary["average"],
        "below_threshold": att_summary["below_threshold"],
        "recent_notifications": recent_notifications,
        "recent_activity": _build_recent_activity(),
    }


def _build_recent_activity() -> list[dict]:
    """Combines recent gate-pass decisions into a simple activity feed."""
    decided = [
        gp for gp in mock_data.MOCK_GATEPASSES
        if gp["status"] != "PENDING" and gp["decided_at"]
    ]
    decided.sort(key=lambda gp: gp["decided_at"], reverse=True)
    activity = []
    for gp in decided[:5]:
        verb = "Approved" if gp["status"] == "APPROVED" else "Rejected"
        activity.append({
            "text": f"{verb} gate pass for {gp['student_name']} ({gp['student_id']})",
            "timestamp": gp["decided_at"],
        })
    return activity
