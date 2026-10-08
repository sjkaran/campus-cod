"""
Gate-pass service — the API boundary for gate-pass operations.

UI (ui/gatepass.py) calls only these functions. In API mode they call
api/api_client.py; in mock mode they read/write mock/mock_data.py.
No UI code changes when that switch happens.
"""

from datetime import datetime

from config.settings import DATA_SOURCE_MODE
from models.gatepass import GatePassRequest
from mock import mock_data


def _to_gp_dict(r: dict) -> dict:
    """Map a backend gate-pass response to the fields GatePassRequest expects."""
    return {
        "request_id": str(r.get("id", "")),
        "student_id": r.get("student_public_id", ""),
        "student_name": r.get("student_name", ""),
        "department": r.get("department_name", r.get("department_code", "")),
        "destination": r.get("destination", ""),
        "reason": r.get("reason", ""),
        "departure_date": r.get("departure_date", ""),
        "departure_time": r.get("departure_time", ""),
        "expected_return": r.get("return_date", r.get("return_time", "")),
        "status": r.get("status", "PENDING"),
        "rejection_reason": r.get("hod_remarks"),
        "previous_passes_count": r.get("previous_passes_count", 0),
        "previous_pass_note": r.get("previous_pass_note", ""),
        "decided_by": r.get("hod_name"),
        "decided_at": r.get("reviewed_at") or r.get("decided_at"),
    }


def get_pending_gatepasses() -> list[GatePassRequest]:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            rows = api_client.get_pending_gatepasses()
            return [GatePassRequest.from_dict(_to_gp_dict(r)) for r in rows]
        except ApiClientError as e:
            raise RuntimeError(str(e))
    return [
        GatePassRequest.from_dict(gp)
        for gp in mock_data.MOCK_GATEPASSES
        if gp["status"] == "PENDING"
    ]


def get_all_gatepasses() -> list[GatePassRequest]:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            rows = api_client.get_gatepasses()
            return [GatePassRequest.from_dict(_to_gp_dict(r)) for r in rows]
        except ApiClientError as e:
            raise RuntimeError(str(e))
    return [GatePassRequest.from_dict(gp) for gp in mock_data.MOCK_GATEPASSES]


def get_gatepass_details(request_id: str) -> GatePassRequest | None:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            r = api_client.get_gatepass_details(request_id)
            if not r:
                return None
            return GatePassRequest.from_dict(_to_gp_dict(r))
        except ApiClientError as e:
            raise RuntimeError(str(e))
    for gp in mock_data.MOCK_GATEPASSES:
        if gp["request_id"] == request_id:
            return GatePassRequest.from_dict(gp)
    return None


def approve_gatepass(request_id: str, decided_by: str) -> GatePassRequest:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            r = api_client.approve_gatepass(request_id)
            data = r.get("data", r)
            return GatePassRequest.from_dict(_to_gp_dict(data))
        except ApiClientError as e:
            raise RuntimeError(str(e))
    record = mock_data.approve_gatepass_record(request_id, decided_by)
    return GatePassRequest.from_dict(record)


def reject_gatepass(request_id: str, reason: str, decided_by: str) -> GatePassRequest:
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("Rejection reason cannot be empty.")
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            r = api_client.reject_gatepass(request_id, reason)
            data = r.get("data", r)
            return GatePassRequest.from_dict(_to_gp_dict(data))
        except ApiClientError as e:
            raise RuntimeError(str(e))
    record = mock_data.reject_gatepass_record(request_id, reason, decided_by)
    return GatePassRequest.from_dict(record)


def get_today_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            rows = api_client.get_gatepasses({"date_from": today, "date_to": today})
            return len(rows)
        except ApiClientError:
            return 0
    return sum(1 for gp in mock_data.MOCK_GATEPASSES if gp["departure_date"] == today)
