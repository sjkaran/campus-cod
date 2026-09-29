from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS
from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models import Role, User
from app.schemas.analytics import (
    AttendanceAnalyticsResponse, GatePassCounts, GroupAttendance, OverviewResponse,
)
from app.schemas.common import DataResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"], responses=COMMON_ERRORS)

def _dept():
    return Query(None, max_length=16, description="Department code. ADMIN: filter. HOD: must equal own department (else 403).")

_staff = require_roles(Role.ADMIN, Role.HOD, Role.FACULTY)
_mgmt = require_roles(Role.ADMIN, Role.HOD)


@router.get("/overview", response_model=DataResponse[OverviewResponse], summary="Dashboard numbers, scoped to the caller's role")
def overview(department: str | None = _dept(), user: User = Depends(_staff), db: Session = Depends(get_db)):
    return {"data": analytics_service.overview(db, user, department)}


@router.get("/attendance", response_model=DataResponse[AttendanceAnalyticsResponse], summary="Overall attendance and low-attendance students")
def attendance(
    department: str | None = _dept(), semester: int | None = Query(None, ge=1, le=12),
    section: str | None = Query(None, max_length=8), subject: str | None = Query(None, max_length=24, description="Subject code"),
    date_from: date | None = None, date_to: date | None = None,
    threshold: float | None = Query(None, ge=0, le=100, description="Low-attendance cut-off (%)"),
    user: User = Depends(_staff), db: Session = Depends(get_db),
):
    return {"data": analytics_service.attendance(
        db, user, department=department, semester=semester, section=section, subject=subject,
        date_from=date_from, date_to=date_to, threshold=threshold)}


@router.get("/attendance/departments", response_model=DataResponse[list[GroupAttendance]], summary="Attendance per department (ADMIN, HOD)")
def by_department(department: str | None = _dept(), user: User = Depends(_mgmt), db: Session = Depends(get_db)):
    return {"data": analytics_service.by_department(db, user, department)}


@router.get("/attendance/subjects", response_model=DataResponse[list[GroupAttendance]], summary="Attendance per subject")
def by_subject(department: str | None = _dept(), user: User = Depends(_staff), db: Session = Depends(get_db)):
    return {"data": analytics_service.by_subject(db, user, department)}


@router.get("/gatepasses", response_model=DataResponse[GatePassCounts], summary="Gate-pass counts by status (ADMIN, HOD)")
def gatepasses(department: str | None = _dept(), user: User = Depends(_mgmt), db: Session = Depends(get_db)):
    return {"data": analytics_service.gatepasses(db, user, department)}
