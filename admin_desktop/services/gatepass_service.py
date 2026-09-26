"""
Gate-pass service (monitoring only — Admin never approves/rejects here).

Stage 1: getGatePasses()/getGatePassDetails() -> mock.gatepasses
Stage 2: -> ApiClient -> GET /api/gatepasses, GET /api/gatepasses/{id}
"""

from models.gatepass import GatePass
from mock.gatepasses import get_all_gatepasses, get_gatepass_by_id
from mock.students import DEPARTMENTS


def get_gatepasses(department: str = "All", status: str = "All",
                    search: str = "", date_from: str = "", date_to: str = "") -> list[GatePass]:
    """FUTURE API INTEGRATION: GET /api/gatepasses?department=&status=&from=&to=&search="""
    records = get_all_gatepasses()
    search = (search or "").strip().lower()

    def in_range(gp: GatePass) -> bool:
        if date_from and gp.submitted_date < date_from:
            return False
        if date_to and gp.submitted_date > date_to:
            return False
        return True

    def matches(gp: GatePass) -> bool:
        if department != "All" and gp.department != department:
            return False
        if status != "All" and gp.status != status:
            return False
        if not in_range(gp):
            return False
        if search:
            haystack = f"{gp.request_id} {gp.student_id} {gp.student_name}".lower()
            if search not in haystack:
                return False
        return True

    return sorted((gp for gp in records if matches(gp)), key=lambda g: g.submitted_date, reverse=True)


def get_gatepass_details(request_id: str) -> GatePass | None:
    """FUTURE API INTEGRATION: GET /api/gatepasses/{id}"""
    return get_gatepass_by_id(request_id)
