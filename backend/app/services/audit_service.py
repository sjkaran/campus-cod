"""Audit trail. Entries join the caller's transaction, so they commit/rollback with the action."""
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.repositories.user_repository import user_repo

_FORBIDDEN_KEYS = {"password", "password_hash", "token", "access_token", "secret"}


def record(
    db: Session, *, user_id: int | None, action: str, resource_type: str,
    resource_id: int | str | None = None, meta: dict | None = None,
) -> None:
    safe_meta = {k: v for k, v in (meta or {}).items() if k.lower() not in _FORBIDDEN_KEYS} or None
    user_repo.add_audit(
        db,
        AuditLog(
            user_id=user_id, action=action, resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None, meta=safe_meta,
        ),
    )
