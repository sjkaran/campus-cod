from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, paged
from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models import GatePassStatus, Role, User
from app.schemas.common import PagedResponse
from app.schemas.reports import AttendanceReportRow, GatePassReportRow, StudentReportRow
from app.services import report_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/reports", tags=["Reports"], responses=COMMON_ERRORS)

def _dept():
    return Query(None, max_length=16, description="Department code. HOD: must equal own department (else 403).")

def _format():
    return Query("json", alias="format", description="json (paginated) or csv (up to 10,000 rows)")

_mgmt = require_roles(Role.ADMIN, Role.HOD)


def _resolve(fmt: str, params: PageParams) -> PageParams:
    return PageParams(1, report_service.MAX_EXPORT_ROWS) if fmt == "csv" else params


def _respond(fmt: str, name: str, items, total, params, model) -> Response | dict:
    if fmt == "csv":
        cols = list(model.model_fields.keys())
        return Response(
            content=report_service.to_csv(items, cols), media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{name}.csv"'},
        )
    return paged(None, items, total, params)


@router.get("/attendance", response_model=PagedResponse[AttendanceReportRow], summary="Per-student/subject attendance (ADMIN, HOD, FACULTY: own sessions)")
def attendance_report(
    department: str | None = _dept(), semester: int | None = Query(None, ge=1, le=12),
    section: str | None = Query(None, max_length=8), subject: str | None = Query(None, max_length=24, description="Subject code"),
    date_from: date | None = None, date_to: date | None = None, fmt: Literal["json", "csv"] = _format(),
    params: PageParams = Depends(page_params),
    user: User = Depends(require_roles(Role.ADMIN, Role.HOD, Role.FACULTY)), db: Session = Depends(get_db),
):
    p = _resolve(fmt, params)
    items, total = report_service.attendance_report(
        db, user, department=department, semester=semester, section=section, subject=subject,
        date_from=date_from, date_to=date_to, params=p)
    return _respond(fmt, "attendance_report", items, total, p, AttendanceReportRow)


@router.get("/students", response_model=PagedResponse[StudentReportRow], summary="Student roster report (ADMIN, HOD)")
def students_report(
    department: str | None = _dept(), semester: int | None = Query(None, ge=1, le=12),
    section: str | None = Query(None, max_length=8), fmt: Literal["json", "csv"] = _format(),
    params: PageParams = Depends(page_params), user: User = Depends(_mgmt), db: Session = Depends(get_db),
):
    p = _resolve(fmt, params)
    items, total = report_service.students_report(db, user, department=department, semester=semester, section=section, params=p)
    return _respond(fmt, "students_report", items, total, p, StudentReportRow)


@router.get("/gatepasses", response_model=PagedResponse[GatePassReportRow], summary="Gate-pass report (ADMIN, HOD)")
def gatepasses_report(
    department: str | None = _dept(), status: GatePassStatus | None = None,
    date_from: date | None = None, date_to: date | None = None, fmt: Literal["json", "csv"] = _format(),
    params: PageParams = Depends(page_params), user: User = Depends(_mgmt), db: Session = Depends(get_db),
):
    p = _resolve(fmt, params)
    items, total = report_service.gatepass_report(
        db, user, department=department, status=status, date_from=date_from, date_to=date_to, params=p)
    return _respond(fmt, "gatepass_report", items, total, p, GatePassReportRow)
