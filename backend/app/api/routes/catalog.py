"""Read-only reference data used to populate dropdowns in every client."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.repositories.catalog_repository import catalog_repo
from app.schemas.catalog import AcademicClassResponse, DepartmentResponse, SubjectResponse
from app.schemas.common import DataResponse

router = APIRouter(tags=["Catalog"], dependencies=[Depends(get_current_user)], responses=COMMON_ERRORS)


def _dept_id(db: Session, code: str | None) -> int | None:
    if not code:
        return None
    dept = catalog_repo.department_by_code(db, code)
    if dept is None:
        raise NotFoundError("Department not found")
    return dept.id


@router.get("/departments", response_model=DataResponse[list[DepartmentResponse]])
def departments(db: Session = Depends(get_db)):
    return {"data": [DepartmentResponse.model_validate(d) for d in catalog_repo.departments(db)]}


@router.get("/subjects", response_model=DataResponse[list[SubjectResponse]])
def subjects(department: str | None = Query(None, max_length=16), db: Session = Depends(get_db)):
    items = catalog_repo.subjects(db, _dept_id(db, department))
    return {"data": [SubjectResponse.model_validate(s) for s in items]}


@router.get("/academic-classes", response_model=DataResponse[list[AcademicClassResponse]])
def academic_classes(department: str | None = Query(None, max_length=16), db: Session = Depends(get_db)):
    items = catalog_repo.classes(db, _dept_id(db, department))
    return {"data": [AcademicClassResponse.model_validate(c) for c in items]}
