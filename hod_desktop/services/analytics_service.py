"""Analytics service — aggregations for the departmental analytics screen."""

from config.settings import (
    DATA_SOURCE_MODE,
    ATTENDANCE_GOOD_THRESHOLD,
    ATTENDANCE_NORMAL_THRESHOLD,
)
from mock import mock_data


def get_subject_wise_attendance() -> list[dict]:
    """GET /analytics/attendance/subjects"""
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            # Returns {"data": [{"key": ..., "label": ..., "summary": {...}}, ...]}
            rows = api_client.get_data("/analytics/attendance/subjects") or []
            result = []
            for row in rows:
                summary = row.get("summary", {})
                result.append({
                    "subject": row.get("label", row.get("key", "")),
                    "percentage": summary.get("percentage", 0.0),
                    "students": summary.get("total_students", 0),
                })
            return result
        except ApiClientError as e:
            raise RuntimeError(str(e))

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
    """GET /analytics/attendance/departments (semester breakdown via overview)"""
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            rows = api_client.get_data("/analytics/attendance/departments") or []
            result = []
            for row in rows:
                summary = row.get("summary", {})
                # key is typically department code; we use label for display
                result.append({
                    "semester": row.get("label", row.get("key", "")),
                    "percentage": summary.get("percentage", 0.0),
                })
            return result
        except ApiClientError as e:
            raise RuntimeError(str(e))

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
    """Buckets students into Good / Normal / Attention bands."""
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            overview = api_client.get_data("/analytics/overview") or {}
            att = overview.get("attendance", {})
            total = overview.get("students") or 0
            low = overview.get("low_attendance_students") or 0
            overall_pct = att.get("percentage", 0.0)
            # Without per-student breakdown from this endpoint, approximate:
            good = max(0, total - low)
            normal = 0
            return {
                "good": good,
                "normal": normal,
                "attention": low,
                "total": total,
            }
        except ApiClientError as e:
            raise RuntimeError(str(e))

    per_student: dict[str, list] = {}
    for r in mock_data.MOCK_ATTENDANCE:
        per_student.setdefault(r["student_id"], []).append(
            r["present"] / r["classes_held"] * 100
        )

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
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            overview = api_client.get_data("/analytics/overview") or {}
            att = overview.get("attendance", {})
            return round(float(att.get("percentage", 0.0)), 1)
        except ApiClientError as e:
            raise RuntimeError(str(e))

    held = sum(r["classes_held"] for r in mock_data.MOCK_ATTENDANCE)
    present = sum(r["present"] for r in mock_data.MOCK_ATTENDANCE)
    return round((present / held) * 100, 1) if held else 0.0
