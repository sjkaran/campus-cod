"""
Gate-pass service — the API boundary for gate-pass operations.

UI (ui/gatepass.py) calls only these functions. Today they read/write
mock/mock_data.py; in Stage 2 they will call api/api_client.py instead,
governed by config.settings.DATA_SOURCE_MODE. No UI code changes when
that switch happens.
"""

from models.gatepass import GatePassRequest
from mock import mock_data


def get_pending_gatepasses() -> list[GatePassRequest]:
    """Future API: GET /api/gatepasses/pending"""
    return [
        GatePassRequest.from_dict(gp)
        for gp in mock_data.MOCK_GATEPASSES
        if gp["status"] == "PENDING"
    ]


def get_all_gatepasses() -> list[GatePassRequest]:
    """Future API: GET /api/gatepasses (department-scoped)"""
    return [GatePassRequest.from_dict(gp) for gp in mock_data.MOCK_GATEPASSES]


def get_gatepass_details(request_id: str) -> GatePassRequest | None:
    """Future API: GET /api/gatepasses/{id}"""
    for gp in mock_data.MOCK_GATEPASSES:
        if gp["request_id"] == request_id:
            return GatePassRequest.from_dict(gp)
    return None


def approve_gatepass(request_id: str, decided_by: str) -> GatePassRequest:
    """Future API: PATCH /api/gatepasses/{id}/approve"""
    record = mock_data.approve_gatepass_record(request_id, decided_by)
    return GatePassRequest.from_dict(record)


def reject_gatepass(request_id: str, reason: str, decided_by: str) -> GatePassRequest:
    """Future API: PATCH /api/gatepasses/{id}/reject"""
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("Rejection reason cannot be empty.")
    record = mock_data.reject_gatepass_record(request_id, reason, decided_by)
    return GatePassRequest.from_dict(record)


def get_today_count() -> int:
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for gp in mock_data.MOCK_GATEPASSES if gp["departure_date"] == today)
