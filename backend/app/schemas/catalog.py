from app.models.enums import RecordStatus
from app.schemas.common import ORMModel


class DepartmentResponse(ORMModel):
    id: int
    code: str
    name: str
    status: RecordStatus


class SubjectResponse(ORMModel):
    id: int
    code: str
    name: str
    department_id: int
    credits: int
    status: RecordStatus


class AcademicClassResponse(ORMModel):
    id: int
    department_id: int
    department_code: str
    semester: int
    section: str
    academic_year: str
    label: str
    status: RecordStatus
