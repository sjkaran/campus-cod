from datetime import datetime

from app.schemas.common import ORMModel


class AuditLogResponse(ORMModel):
    id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    timestamp: datetime
    meta: dict | None
