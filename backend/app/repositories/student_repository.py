from __future__ import annotations
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import AcademicClass, RecordStatus, Student
from app.utils.pagination import PageParams, paginate


@dataclass
class StudentFilters:
    department_id: int | None = None
    semester: int | None = None
    section: str | None = None
    q: str | None = None


class StudentRepository:
    def get(self, db: Session, pk: int) -> Student | None:
        return db.execute(
            select(Student).options(joinedload(Student.department)).where(Student.id == pk)
        ).scalar_one_or_none()

    def list(self, db: Session, f: StudentFilters, params: PageParams):
        stmt = select(Student).options(joinedload(Student.department)).order_by(Student.student_id)
        if f.department_id is not None:
            stmt = stmt.where(Student.department_id == f.department_id)
        if f.semester is not None:
            stmt = stmt.where(Student.semester == f.semester)
        if f.section:
            stmt = stmt.where(Student.section == f.section.upper())
        if f.q:
            like = f"%{f.q.strip()}%"
            stmt = stmt.where(or_(Student.name.ilike(like), Student.student_id.ilike(like), Student.roll_number.ilike(like)))
        return paginate(db, stmt, params)

    def count(self, db: Session, department_id: int | None = None) -> int:
        stmt = select(func.count(Student.id))
        if department_id is not None:
            stmt = stmt.where(Student.department_id == department_id)
        return int(db.execute(stmt).scalar_one())

    def for_class(self, db: Session, academic_class: AcademicClass) -> list[Student]:
        """Active students belonging to an academic class (dept + semester + section)."""
        stmt = select(Student).where(
            Student.department_id == academic_class.department_id,
            Student.semester == academic_class.semester,
            Student.section == academic_class.section,
            Student.status == RecordStatus.ACTIVE,
        )
        return list(db.execute(stmt).scalars())

    def get_by_public_ids(self, db: Session, public_ids: list[str]) -> list[Student]:
        return list(db.execute(select(Student).where(Student.student_id.in_(public_ids))).scalars())


student_repo = StudentRepository()
