"""
Mock analytics aggregation.

FUTURE API INTEGRATION
Replace this module's data source with:
    GET /api/analytics/overview
    GET /api/analytics/attendance
    GET /api/analytics/attendance/departments
    GET /api/analytics/attendance/subjects
    GET /api/analytics/gatepasses

This module derives analytics from the other mock datasets so the numbers
stay internally consistent (e.g. dashboard KPIs match the Students screen).
"""

from collections import Counter

from models.analytics import AnalyticsOverview
from mock.students import get_all_students
from mock.attendance import get_all_attendance, compute_summary
from mock.gatepasses import get_all_gatepasses
from mock.notifications import get_all_notifications
from utils.helpers import safe_divide


def get_overview() -> AnalyticsOverview:
    students = get_all_students()
    attendance_records = get_all_attendance()
    gatepasses = get_all_gatepasses()
    notifications = get_all_notifications()
    summary = compute_summary()

    students_by_department = dict(Counter(s.department for s in students))
    students_by_semester = dict(Counter(s.semester for s in students))
    active = len([s for s in students if s.is_active])
    inactive = len(students) - active

    subject_totals: dict[str, list[int]] = {}
    for r in attendance_records:
        subject_totals.setdefault(r.subject, [0, 0])
        subject_totals[r.subject][0] += r.present
        subject_totals[r.subject][1] += r.classes_held
    attendance_by_subject = {
        subj: round(safe_divide(p, h) * 100, 1) for subj, (p, h) in subject_totals.items()
    }

    low_attendance_students = summary.students_below_threshold

    gp_pending = len([g for g in gatepasses if g.status == "PENDING"])
    gp_approved = len([g for g in gatepasses if g.status == "APPROVED"])
    gp_rejected = len([g for g in gatepasses if g.status == "REJECTED"])

    notif_active = len([n for n in notifications if n.status == "ACTIVE"])
    notif_by_audience = dict(Counter(n.audience for n in notifications))

    return AnalyticsOverview(
        total_students=len(students),
        students_by_department=students_by_department,
        students_by_semester=students_by_semester,
        active_students=active,
        inactive_students=inactive,
        overall_attendance=summary.overall_percentage,
        attendance_by_department=summary.department_averages,
        attendance_by_semester=summary.semester_averages,
        attendance_by_subject=attendance_by_subject,
        low_attendance_students=low_attendance_students,
        gatepass_total=len(gatepasses),
        gatepass_pending=gp_pending,
        gatepass_approved=gp_approved,
        gatepass_rejected=gp_rejected,
        notifications_published=len(notifications),
        notifications_active=notif_active,
        notifications_by_audience=notif_by_audience,
    )
