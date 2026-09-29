from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, ok, paged
from app.core.dependencies import current_student, get_current_user, require_roles
from app.database.database import get_db
from app.models import Role, Student, User
from app.schemas.common import DataResponse, PagedResponse
from app.schemas.student import StudentAttendanceResponse, StudentResponse
from app.services import student_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/students", tags=["Students"], responses=COMMON_ERRORS)


@router.get("", response_model=PagedResponse[StudentResponse], summary="List students (ADMIN: all, HOD: own department)")
def list_students(
    department: str | None = Query(None, max_length=16, description="Department code, e.g. CSE"),
    semester: int | None = Query(None, ge=1, le=12),
    section: str | None = Query(None, max_length=8),
    q: str | None = Query(None, max_length=64, description="Search name / student ID / roll number"),
    params: PageParams = Depends(page_params),
    user: User = Depends(require_roles(Role.ADMIN, Role.HOD)),
    db: Session = Depends(get_db),
):
    items, total = student_service.list_students(
        db, user, department=department, semester=semester, section=section, q=q, params=params
    )
    return paged(StudentResponse, items, total, params)


@router.get("/me", response_model=DataResponse[StudentResponse], summary="Own profile (STUDENT)")
def my_profile(student: Student = Depends(current_student)):
    return ok(StudentResponse, student)


@router.get(
    "/me/attendance", response_model=DataResponse[StudentAttendanceResponse],
    summary="Own attendance with overall and per-subject percentages (STUDENT)",
)
def my_attendance(student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return {"data": student_service.my_attendance(db, student)}


@router.get(
    "/{student_pk}", response_model=DataResponse[StudentResponse],
    summary="Get one student (ADMIN any, HOD own department, STUDENT only self)",
)
def get_student(
    student_pk: int,
    user: User = Depends(require_roles(Role.ADMIN, Role.HOD, Role.STUDENT)),
    db: Session = Depends(get_db),
):
    return ok(StudentResponse, student_service.get_student(db, user, student_pk))
