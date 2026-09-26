"""
Attendance service.

Stage 1: getAttendance()/getAttendanceSummary() -> mock.attendance
Stage 2: -> ApiClient -> GET /api/attendance, GET /api/attendance/summary
"""

from models.attendance import AttendanceRecord, AttendanceSummary
from mock.attendance import get_all_attendance, compute_summary, SUBJECTS_BY_DEPARTMENT
from mock.students import DEPARTMENTS, SECTIONS


def get_all_subjects() -> list[str]:
    subjects: set[str] = set()
    for subs in SUBJECTS_BY_DEPARTMENT.values():
        subjects.update(subs)
    return sorted(subjects)


def get_attendance(department: str = "All", semester: str = "All", section: str = "All",
                    subject: str = "All", status: str = "All",
                    search: str = "") -> list[AttendanceRecord]:
    """FUTURE API INTEGRATION: GET /api/attendance?department=&semester=&section=&subject=&status="""
    records = get_all_attendance()
    search = (search or "").strip().lower()

    def status_matches(r: AttendanceRecord) -> bool:
        if status == "All":
            return True
        if status == "Below Threshold":
            return 65.0 <= r.percentage < 75.0
        if status == "Critical":
            return r.percentage < 65.0
        if status == "Healthy":
            return r.percentage >= 75.0
        return True

    def matches(r: AttendanceRecord) -> bool:
        if department != "All" and r.department != department:
            return False
        if semester != "All" and str(r.semester) != str(semester):
            return False
        if section != "All" and r.section != section:
            return False
        if subject != "All" and r.subject != subject:
            return False
        if not status_matches(r):
            return False
        if search:
            haystack = f"{r.student_id} {r.student_name}".lower()
            if search not in haystack:
                return False
        return True

    return [r for r in records if matches(r)]


def get_attendance_summary() -> AttendanceSummary:
    """FUTURE API INTEGRATION: GET /api/attendance/summary"""
    return compute_summary()
