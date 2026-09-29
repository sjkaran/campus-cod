from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator

from app.models.enums import GatePassStatus
from app.schemas.common import ORMModel


class GatePassCreate(BaseModel):
    """Students may only supply these fields. Status/HOD/review data are backend-controlled."""
    model_config = {"extra": "forbid"}

    destination: str = Field(min_length=2, max_length=200)
    reason: str = Field(min_length=5, max_length=1000)
    departure_date: date
    departure_time: time
    return_date: date
    return_time: time

    @model_validator(mode="after")
    def _strip(self):
        self.destination = self.destination.strip()
        self.reason = self.reason.strip()
        if len(self.destination) < 2 or len(self.reason) < 5:
            raise ValueError("destination/reason too short")
        return self


class GatePassApprove(BaseModel):
    remarks: str | None = Field(default=None, max_length=1000)


class GatePassReject(BaseModel):
    remarks: str = Field(min_length=3, max_length=1000)

    @model_validator(mode="after")
    def _strip(self):
        self.remarks = self.remarks.strip()
        if len(self.remarks) < 3:
            raise ValueError("remarks are required when rejecting")
        return self


class GatePassResponse(ORMModel):
    id: int
    student_id: int
    student_public_id: str
    student_name: str
    department_code: str
    destination: str
    reason: str
    departure_date: date
    departure_time: time
    return_date: date
    return_time: time
    status: GatePassStatus
    hod_id: int | None
    hod_name: str | None
    hod_remarks: str | None
    created_at: datetime
    reviewed_at: datetime | None
