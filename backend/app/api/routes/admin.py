from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, ok, paged
from app.core.dependencies import require_admin
from app.database.database import get_db
from app.models import User
from app.repositories.user_repository import user_repo
from app.schemas.audit import AuditLogResponse
from app.schemas.common import DataResponse, PagedResponse
from app.schemas.faculty import AdminResponse
from app.core.exceptions import ForbiddenError
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/admin", tags=["Admin"], responses=COMMON_ERRORS)


@router.get("/me", response_model=DataResponse[AdminResponse], summary="Own profile")
def my_profile(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    admin = user_repo.admin_for_user(db, user.id)
    if admin is None:
        raise ForbiddenError("Admin profile not found")
    return ok(AdminResponse, admin)


@router.get("/audit-logs", response_model=PagedResponse[AuditLogResponse], summary="Audit trail (ADMIN)")
def audit_logs(
    action: str | None = Query(None, max_length=64, description="e.g. GATEPASS_APPROVED"),
    params: PageParams = Depends(page_params),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    items, total = user_repo.list_audit(db, params, action)
    return paged(AuditLogResponse, items, total, params)
