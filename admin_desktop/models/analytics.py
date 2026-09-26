"""Data model for aggregate institution-level analytics."""

from dataclasses import dataclass, field


@dataclass
class AnalyticsOverview:
    total_students: int
    students_by_department: dict
    students_by_semester: dict
    active_students: int
    inactive_students: int

    overall_attendance: float
    attendance_by_department: dict
    attendance_by_semester: dict
    attendance_by_subject: dict
    low_attendance_students: int

    gatepass_total: int
    gatepass_pending: int
    gatepass_approved: int
    gatepass_rejected: int

    notifications_published: int
    notifications_active: int
    notifications_by_audience: dict
