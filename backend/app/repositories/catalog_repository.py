from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AcademicClass, Department, Subject


class CatalogRepository:
    def departments(self, db: Session) -> list[Department]:
        return list(db.execute(select(Department).order_by(Department.code)).scalars())

    def department_by_code(self, db: Session, code: str) -> Department | None:
        return db.execute(select(Department).where(Department.code == code.upper())).scalar_one_or_none()

    def subjects(self, db: Session, department_id: int | None = None) -> list[Subject]:
        stmt = select(Subject).order_by(Subject.code)
        if department_id:
            stmt = stmt.where(Subject.department_id == department_id)
        return list(db.execute(stmt).scalars())

    def subject_by_code(self, db: Session, code: str) -> Subject | None:
        return db.execute(select(Subject).where(Subject.code == code.upper())).scalar_one_or_none()

    def get_subject(self, db: Session, subject_id: int) -> Subject | None:
        return db.get(Subject, subject_id)

    def classes(self, db: Session, department_id: int | None = None) -> list[AcademicClass]:
        stmt = (
            select(AcademicClass)
            .options(joinedload(AcademicClass.department))
            .order_by(AcademicClass.department_id, AcademicClass.semester, AcademicClass.section)
        )
        if department_id:
            stmt = stmt.where(AcademicClass.department_id == department_id)
        return list(db.execute(stmt).scalars())

    def get_class(self, db: Session, class_id: int) -> AcademicClass | None:
        return db.get(AcademicClass, class_id)


catalog_repo = CatalogRepository()
