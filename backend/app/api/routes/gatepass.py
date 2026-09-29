from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, ok, paged
from app.core.dependencies import current_hod, current_student, require_roles
from app.database.database import get_db
from app.models import GatePassStatus, Hod, Role, Student, User
from app.schemas.common import DataResponse, ErrorResponse, PagedResponse
from app.schemas.gatepass import GatePassApprove, GatePassCreate, GatePassReject, GatePassResponse
from app.services import gatepass_service
from app.services.access import narrow_department, resolve_scope
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/gatepasses", tags=["Gate Pass"], responses=COMMON_ERRORS)
_conflict = {409: {"model": ErrorResponse, "description": "Gate pass already reviewed / not pending"}}


@router.post("", status_code=201, response_model=DataResponse[GatePassResponse], summary="Request a gate pass (STUDENT)")
def create(body: GatePassCreate, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return ok(GatePassResponse, gatepass_service.create(db, student, body))


@router.get("/my", response_model=PagedResponse[GatePassResponse], summary="Own gate passes (STUDENT)")
def my_gatepasses(
    status: GatePassStatus | None = None,
    params: PageParams = Depends(page_params),
    student: Student = Depends(current_student), db: Session = Depends(get_db),
):
    items, total = gatepass_service.list_my(db, student, status, params)
    return paged(GatePassResponse, items, total, params)


@router.get("/pending", response_model=PagedResponse[GatePassResponse], summary="Pending requests in own department, oldest first (HOD)")
def pending(params: PageParams = Depends(page_params), hod: Hod = Depends(current_hod), db: Session = Depends(get_db)):
    items, total = gatepass_service.list_pending(db, hod, params)
    return paged(GatePassResponse, items, total, params)


@router.get("", response_model=PagedResponse[GatePassResponse], summary="All gate passes (ADMIN: institution, HOD: own department)")
def list_all(
    status: GatePassStatus | None = None,
    department: str | None = Query(None, max_length=16, description="Department code (ADMIN only; HOD is pinned)"),
    date_from: date | None = None, date_to: date | None = None,
    params: PageParams = Depends(page_params),
    user: User = Depends(require_roles(Role.ADMIN, Role.HOD)), db: Session = Depends(get_db),
):
    scope = resolve_scope(db, user)
    dept_id = narrow_department(db, scope, department)
    items, total = gatepass_service.list_for_staff(db, user, status, dept_id, params, date_from, date_to)
    return paged(GatePassResponse, items, total, params)


@router.get("/{gatepass_id}", response_model=DataResponse[GatePassResponse], summary="One gate pass (owner STUDENT, HOD of department, ADMIN)")
def get_one(
    gatepass_id: int,
    user: User = Depends(require_roles(Role.STUDENT, Role.HOD, Role.ADMIN)), db: Session = Depends(get_db),
):
    return ok(GatePassResponse, gatepass_service.get_for_user(db, user, gatepass_id))


@router.patch("/{gatepass_id}/approve", response_model=DataResponse[GatePassResponse], responses=_conflict,
              summary="Approve a PENDING request in own department (HOD)")
def approve(gatepass_id: int, body: GatePassApprove | None = None, hod: Hod = Depends(current_hod), db: Session = Depends(get_db)):
    return ok(GatePassResponse, gatepass_service.approve(db, hod, gatepass_id, body))


@router.patch("/{gatepass_id}/reject", response_model=DataResponse[GatePassResponse], responses=_conflict,
              summary="Reject a PENDING request; remarks are required (HOD)")
def reject(gatepass_id: int, body: GatePassReject, hod: Hod = Depends(current_hod), db: Session = Depends(get_db)):
    return ok(GatePassResponse, gatepass_service.reject(db, hod, gatepass_id, body))


@router.patch("/{gatepass_id}/cancel", response_model=DataResponse[GatePassResponse], responses=_conflict,
              summary="Cancel own PENDING request (STUDENT)")
def cancel(gatepass_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return ok(GatePassResponse, gatepass_service.cancel(db, student, gatepass_id))
