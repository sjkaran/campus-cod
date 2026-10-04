"""
Gate-pass service — Stage 2 (live backend). Monitoring only — Admin never
approves/rejects here; that's exclusively the HOD role's authority on the
backend (enforced server-side, not just hidden in this UI).

GET /gatepasses, GET /gatepasses/{id}
"""

from models.gatepass import GatePass
from api.api_client import api_client, ApiClientError
from services import student_service


def _to_gatepass(row: dict) -> GatePass:
    return GatePass(
        request_id=f"GP{row['id']:04d}",
        student_id=row.get("student_public_id", ""),
        student_name=row.get("student_name", ""),
        department=student_service.name_for_department_code(row.get("department_code")),
        destination=row.get("destination", ""),
        reason=row.get("reason", ""),
        departure_date=row.get("departure_date", ""),
        return_date=row.get("return_date", ""),
        submitted_date=(row.get("created_at") or "")[:10],
        status=row.get("status", ""),
        reviewing_authority=row.get("hod_name") or "—",
        remarks=row.get("hod_remarks") or "",
        pk=row["id"],
    )


def get_gatepasses(department: str = "All", status: str = "All",
                    search: str = "", date_from: str = "", date_to: str = "") -> list[GatePass]:
    """FUTURE (now live): GET /gatepasses?department=&status=&date_from=&date_to="""
    params = {
        "department": student_service.code_for_department_name(department) if department != "All" else None,
        "status": status if status != "All" else None,
        "date_from": date_from or None,
        "date_to": date_to or None,
    }
    try:
        rows = api_client.get_all_pages("/gatepasses", params=params)
    except ApiClientError:
        return []

    gatepasses = [_to_gatepass(r) for r in rows]
    search = (search or "").strip().lower()
    if search:
        gatepasses = [g for g in gatepasses
                      if search in f"{g.request_id} {g.student_id} {g.student_name}".lower()]
    gatepasses.sort(key=lambda g: g.submitted_date, reverse=True)
    return gatepasses


def get_gatepass_details(request_id: str) -> GatePass | None:
    """FUTURE (now live): GET /gatepasses/{id}. `request_id` is our display
    form "GP0005"; the backend wants the bare integer id."""
    digits = request_id.upper().replace("GP", "", 1)
    try:
        pk = int(digits)
    except ValueError:
        return None
    try:
        row = api_client.get_data(f"/gatepasses/{pk}")
    except ApiClientError:
        return None
    return _to_gatepass(row) if row else None
