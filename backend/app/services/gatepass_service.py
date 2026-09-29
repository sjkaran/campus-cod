import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models import GatePass, GatePassStatus, Hod, RecordStatus, Role, Student, User
from app.repositories.gatepass_repository import gatepass_repo
from app.repositories.user_repository import user_repo
from app.schemas.gatepass import GatePassApprove, GatePassCreate, GatePassReject
from app.services import audit_service
from app.utils.pagination import PageParams
from app.utils.timeutil import campus_now, combine

log = logging.getLogger("app.gatepass")
MAX_TRIP = timedelta(days=30)


def create(db: Session, student: Student, data: GatePassCreate) -> GatePass:
    if student.status != RecordStatus.ACTIVE:
        raise ForbiddenError("Inactive students cannot request gate passes")
    departure = combine(data.departure_date, data.departure_time)
    returning = combine(data.return_date, data.return_time)
    if departure < campus_now() - timedelta(minutes=5):
        raise BadRequestError("Departure cannot be in the past")
    if returning <= departure:
        raise BadRequestError("Return must be after departure")
    if returning - departure > MAX_TRIP:
        raise BadRequestError("A gate pass cannot span more than 30 days")

    # Status, HOD and review fields are NEVER taken from the client.
    gp = GatePass(
        student_id=student.id, destination=data.destination, reason=data.reason,
        departure_date=data.departure_date, departure_time=data.departure_time,
        return_date=data.return_date, return_time=data.return_time,
        status=GatePassStatus.PENDING,
    )
    gatepass_repo.add(db, gp)
    audit_service.record(db, user_id=student.user_id, action="GATEPASS_CREATED", resource_type="gate_pass", resource_id=gp.id)
    db.commit()
    return gatepass_repo.get(db, gp.id)


def list_my(db: Session, student: Student, status: GatePassStatus | None, params: PageParams):
    return gatepass_repo.list(db, params, student_id=student.id, status=status)


def list_pending(db: Session, hod: Hod, params: PageParams):
    return gatepass_repo.list(db, params, department_id=hod.department_id, status=GatePassStatus.PENDING, oldest_first=True)


def list_for_staff(
    db: Session, user: User, status: GatePassStatus | None, department_id: int | None, params: PageParams,
    date_from: date | None = None, date_to: date | None = None,
):
    """ADMIN: institution-wide. HOD: pinned to own department (department_id already validated)."""
    return gatepass_repo.list(db, params, department_id=department_id, status=status, date_from=date_from, date_to=date_to)


def get_for_user(db: Session, user: User, gp_id: int) -> GatePass:
    gp = gatepass_repo.get(db, gp_id)
    allowed = False
    if gp is not None:
        if user.role == Role.ADMIN:
            allowed = True
        elif user.role == Role.STUDENT:
            allowed = gp.student.user_id == user.id
        elif user.role == Role.HOD:
            hod = user_repo.hod_for_user(db, user.id)
            allowed = bool(hod and hod.department_id == gp.student.department_id)
    if not allowed:
        raise NotFoundError("Gate pass not found")
    return gp


def _review(db: Session, hod: Hod, gp_id: int, new_status: GatePassStatus, remarks: str | None) -> GatePass:
    """Single transaction: lock row -> verify authority + state -> set status/HOD/timestamp."""
    gp = gatepass_repo.get(db, gp_id, for_update=True)
    if gp is None or gp.student.department_id != hod.department_id:
        raise NotFoundError("Gate pass not found")  # other departments' requests are invisible
    if gp.status != GatePassStatus.PENDING:
        raise ConflictError("Gate pass has already been reviewed.")
    gp.status = new_status
    gp.hod_id = hod.id
    gp.hod_remarks = remarks
    gp.reviewed_at = datetime.now(timezone.utc)
    audit_service.record(
        db, user_id=hod.user_id, action=f"GATEPASS_{new_status.value}", resource_type="gate_pass",
        resource_id=gp.id, meta={"student_id": gp.student_id},
    )
    db.commit()
    log.info("gatepass_%s id=%s hod_id=%s", new_status.value.lower(), gp.id, hod.id)
    return gatepass_repo.get(db, gp.id)


def approve(db: Session, hod: Hod, gp_id: int, data: GatePassApprove | None) -> GatePass:
    return _review(db, hod, gp_id, GatePassStatus.APPROVED, data.remarks if data else None)


def reject(db: Session, hod: Hod, gp_id: int, data: GatePassReject) -> GatePass:
    return _review(db, hod, gp_id, GatePassStatus.REJECTED, data.remarks)


def cancel(db: Session, student: Student, gp_id: int) -> GatePass:
    gp = gatepass_repo.get(db, gp_id, for_update=True)
    if gp is None or gp.student_id != student.id:
        raise NotFoundError("Gate pass not found")
    if gp.status != GatePassStatus.PENDING:
        raise ConflictError("Only pending gate passes can be cancelled.")
    gp.status = GatePassStatus.CANCELLED
    audit_service.record(db, user_id=student.user_id, action="GATEPASS_CANCELLED", resource_type="gate_pass", resource_id=gp.id)
    db.commit()
    return gatepass_repo.get(db, gp.id)
