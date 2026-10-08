"""
Dashboard service — pulls a small summary from the other services so
ui/dashboard.py has a single call to make instead of orchestrating
four separate service imports itself.
"""

from config.settings import DATA_SOURCE_MODE
from services import gatepass_service, attendance_service


def get_dashboard_summary() -> dict:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            summary = api_client.get_dashboard_summary()
            if summary:
                return {
                    "pending_passes": summary.get("pending_passes", 0),
                    "today_passes": summary.get("today_passes", 0),
                    "department_attendance": summary.get("department_attendance", 0.0),
                    "below_threshold": summary.get("below_threshold", 0),
                    "recent_notifications": summary.get("recent_notifications", []),
                    "recent_activity": summary.get("recent_activity", []),
                }
        except ApiClientError as e:
            if getattr(e, "status_code", None) != 404:
                raise RuntimeError(str(e))
            # 404 — endpoint not yet implemented; fall through to compose locally

        # Compose from individual service calls when /hod/dashboard is absent
        return _compose_from_services()

    # mock path
    from mock import mock_data
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
        "recent_activity": _build_mock_recent_activity(),
    }


def _compose_from_services() -> dict:
    """Compose dashboard data from individual API service calls (fallback)."""
    from api.api_client import ApiClientError

    try:
        pending = gatepass_service.get_pending_gatepasses()
        pending_count = len(pending)
    except (RuntimeError, ApiClientError):
        pending_count = 0

    try:
        today_count = gatepass_service.get_today_count()
    except (RuntimeError, ApiClientError):
        today_count = 0

    try:
        att_summary = attendance_service.get_department_summary()
    except (RuntimeError, ApiClientError):
        att_summary = {"average": 0.0, "below_threshold": 0}

    return {
        "pending_passes": pending_count,
        "today_passes": today_count,
        "department_attendance": att_summary["average"],
        "below_threshold": att_summary["below_threshold"],
        "recent_notifications": [],
        "recent_activity": [],
    }


def _build_mock_recent_activity() -> list[dict]:
    """Combines recent gate-pass decisions into a simple activity feed (mock mode)."""
    from mock import mock_data
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
