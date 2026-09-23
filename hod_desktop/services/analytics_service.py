"""Analytics service — aggregations for the departmental analytics screen."""

from config.settings import ATTENDANCE_GOOD_THRESHOLD, ATTENDANCE_NORMAL_THRESHOLD
from mock import mock_data


def get_subject_wise_attendance() -> list[dict]:
    """Future API: GET /api/analytics/department/subjects"""
    by_subject: dict[str, list] = {}
    for r in mock_data.MOCK_ATTENDANCE:
        by_subject.setdefault(r["subject"], []).append(r)

    result = []
    for subject, records in sorted(by_subject.items()):
        held = sum(r["classes_held"] for r in records)
        present = sum(r["present"] for r in records)
        pct = round((present / held) * 100, 1) if held else 0.0
        result.append({"subject": subject, "percentage": pct, "students": len(records)})
    return result


def get_semester_wise_attendance() -> list[dict]:
    """Future API: GET /api/analytics/department/attendance (semester breakdown)"""
    by_sem: dict[int, list] = {}
    for r in mock_data.MOCK_ATTENDANCE:
        by_sem.setdefault(r["semester"], []).append(r)

    result = []
    for sem, records in sorted(by_sem.items()):
        held = sum(r["classes_held"] for r in records)
        present = sum(r["present"] for r in records)
        pct = round((present / held) * 100, 1) if held else 0.0
        result.append({"semester": sem, "percentage": pct})
    return result


def get_attendance_distribution() -> dict:
    """
    Buckets students into Good / Normal / Attention bands based on
    each student's overall average attendance across subjects.
    """
    per_student: dict[str, list] = {}
    for r in mock_data.MOCK_ATTENDANCE:
        per_student.setdefault(r["student_id"], []).append(r["present"] / r["classes_held"] * 100)

    good = normal = low = 0
    for pcts in per_student.values():
        avg = sum(pcts) / len(pcts)
        if avg >= ATTENDANCE_GOOD_THRESHOLD:
            good += 1
        elif avg >= ATTENDANCE_NORMAL_THRESHOLD:
            normal += 1
        else:
            low += 1
    return {"good": good, "normal": normal, "attention": low, "total": len(per_student)}


def get_department_average() -> float:
    held = sum(r["classes_held"] for r in mock_data.MOCK_ATTENDANCE)
    present = sum(r["present"] for r in mock_data.MOCK_ATTENDANCE)
    return round((present / held) * 100, 1) if held else 0.0
