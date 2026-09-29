from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import GatePass, GatePassStatus, Student
from app.utils.pagination import PageParams, paginate

_LOAD = (joinedload(GatePass.student).joinedload(Student.department), joinedload(GatePass.hod))


class GatePassRepository:
    def add(self, db: Session, gp: GatePass) -> GatePass:
        db.add(gp)
        db.flush()
        return gp

    def get(self, db: Session, gp_id: int, *, for_update: bool = False) -> GatePass | None:
        stmt = select(GatePass).where(GatePass.id == gp_id)
        if for_update:
            # Row lock serialises concurrent reviews; `of=` keeps it valid on PostgreSQL.
            stmt = stmt.with_for_update(of=GatePass)
        else:
            stmt = stmt.options(*_LOAD)
        return db.execute(stmt).scalar_one_or_none()

    def list(
        self, db: Session, params: PageParams, *, student_id: int | None = None,
        department_id: int | None = None, status: GatePassStatus | None = None,
        oldest_first: bool = False, date_from=None, date_to=None,
    ):
        stmt = select(GatePass).join(Student, Student.id == GatePass.student_id).options(*_LOAD)
        if student_id is not None:
            stmt = stmt.where(GatePass.student_id == student_id)
        if department_id is not None:
            stmt = stmt.where(Student.department_id == department_id)
        if status is not None:
            stmt = stmt.where(GatePass.status == status)
        if date_from is not None:
            stmt = stmt.where(GatePass.departure_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(GatePass.departure_date <= date_to)
        stmt = stmt.order_by(GatePass.created_at.asc() if oldest_first else GatePass.created_at.desc(), GatePass.id)
        return paginate(db, stmt, params)

    def count_by_status(self, db: Session, department_id: int | None = None) -> dict[GatePassStatus, int]:
        stmt = select(GatePass.status, func.count(GatePass.id)).join(Student, Student.id == GatePass.student_id)
        if department_id is not None:
            stmt = stmt.where(Student.department_id == department_id)
        return {status: n for status, n in db.execute(stmt.group_by(GatePass.status)).all()}


gatepass_repo = GatePassRepository()
