from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AudienceType, NotificationStatus, Priority
from app.schemas.common import ORMModel


class NotificationTargetInput(BaseModel):
    department_code: str | None = Field(default=None, max_length=16)
    semester: int | None = Field(default=None, ge=1, le=12)
    section: str | None = Field(default=None, max_length=8)
    student_id: str | None = Field(default=None, max_length=32, description="Public student ID")


class NotificationCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    priority: Priority = Priority.NORMAL
    audience_type: AudienceType
    expires_at: datetime | None = None
    targets: list[NotificationTargetInput] = Field(default_factory=list, max_length=50)


class NotificationTargetResponse(ORMModel):
    department_id: int | None
    semester: int | None
    section: str | None
    student_id: int | None


class NotificationResponse(ORMModel):
    id: int
    title: str
    message: str
    priority: Priority
    audience_type: AudienceType
    created_by: int
    author_name: str | None = None
    created_at: datetime
    expires_at: datetime | None
    status: NotificationStatus
    is_read: bool | None = None  # only populated for student views


class NotificationDetail(NotificationResponse):
    targets: list[NotificationTargetResponse] = []


class ReadResult(BaseModel):
    notification_id: int
    is_read: bool
