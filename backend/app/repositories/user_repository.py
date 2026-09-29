from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Admin, AuditLog, Faculty, Hod, Student, User
from app.utils.pagination import PageParams, paginate


class UserRepository:
    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.execute(select(User).where(User.username == username)).scalar_one_or_none()

    def get(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def student_for_user(self, db: Session, user_id: int) -> Student | None:
        return db.execute(select(Student).where(Student.user_id == user_id)).scalar_one_or_none()

    def faculty_for_user(self, db: Session, user_id: int) -> Faculty | None:
        return db.execute(select(Faculty).where(Faculty.user_id == user_id)).scalar_one_or_none()

    def hod_for_user(self, db: Session, user_id: int) -> Hod | None:
        return db.execute(select(Hod).where(Hod.user_id == user_id)).scalar_one_or_none()

    def admin_for_user(self, db: Session, user_id: int) -> Admin | None:
        return db.execute(select(Admin).where(Admin.user_id == user_id)).scalar_one_or_none()

    def count_faculty(self, db: Session, department_id: int | None = None) -> int:
        stmt = select(func.count(Faculty.id))
        if department_id is not None:
            stmt = stmt.where(Faculty.department_id == department_id)
        return int(db.execute(stmt).scalar_one())

    def display_names(self, db: Session, user_ids: list[int]) -> dict[int, str]:
        """Best-effort real names for users, resolved from whichever profile table matches."""
        names: dict[int, str] = {}
        if not user_ids:
            return names
        for model in (Student, Faculty, Hod, Admin):
            rows = db.execute(select(model.user_id, model.name).where(model.user_id.in_(user_ids))).all()
            names.update({uid: name for uid, name in rows})
        return names

    # --- audit -------------------------------------------------------------
    def add_audit(self, db: Session, entry: AuditLog) -> None:
        db.add(entry)

    def list_audit(self, db: Session, params: PageParams, action: str | None = None):
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
        if action:
            stmt = stmt.where(AuditLog.action == action)
        return paginate(db, stmt, params)


user_repo = UserRepository()
