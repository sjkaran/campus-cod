from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, paged
from app.core.dependencies import current_student, require_roles
from app.database.database import get_db
from app.models import Role, Student, User
from app.schemas.common import DataResponse, PagedResponse
from app.schemas.notification import NotificationCreate, NotificationDetail, NotificationResponse, ReadResult
from app.services import notification_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/notifications", tags=["Notifications"], responses=COMMON_ERRORS)


@router.get("", response_model=PagedResponse[NotificationResponse], summary="Notifications targeted at me (STUDENT)")
def my_notifications(
    unread: bool | None = Query(None, description="true = unread only, false = read only"),
    params: PageParams = Depends(page_params),
    student: Student = Depends(current_student), db: Session = Depends(get_db),
):
    items, total = notification_service.list_for_student(db, student, unread, params)
    return paged(None, items, total, params)


@router.post(
    "", status_code=201, response_model=DataResponse[NotificationDetail],
    summary="Publish a notification (ADMIN: any audience; HOD: own department only)",
)
def publish(body: NotificationCreate, user: User = Depends(require_roles(Role.ADMIN, Role.HOD)), db: Session = Depends(get_db)):
    return {"data": notification_service.publish(db, user, body)}


@router.get("/admin", response_model=PagedResponse[NotificationResponse], summary="All published notifications (ADMIN)")
def admin_list(params: PageParams = Depends(page_params), user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    items, total = notification_service.list_published(db, user, params, only_mine=False)
    return paged(None, items, total, params)


@router.get("/created-by-me", response_model=PagedResponse[NotificationResponse], summary="Notifications I published (ADMIN, HOD)")
def created_by_me(params: PageParams = Depends(page_params), user: User = Depends(require_roles(Role.ADMIN, Role.HOD)), db: Session = Depends(get_db)):
    items, total = notification_service.list_published(db, user, params, only_mine=True)
    return paged(None, items, total, params)


@router.patch("/{notification_id}/read", response_model=DataResponse[ReadResult], summary="Mark as read for me (STUDENT)")
def mark_read(notification_id: int, student: Student = Depends(current_student), db: Session = Depends(get_db)):
    return {"data": notification_service.mark_read(db, student, notification_id)}
