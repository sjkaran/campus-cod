from app.models.enums import RecordStatus
from app.schemas.catalog import AcademicClassResponse, SubjectResponse
from app.schemas.common import ORMModel


class AssignmentResponse(ORMModel):
    id: int
    subject: SubjectResponse
    academic_class: AcademicClassResponse


class FacultyResponse(ORMModel):
    id: int
    faculty_id: str
    name: str
    email: str
    department_id: int
    department_code: str
    status: RecordStatus
    assignments: list[AssignmentResponse] = []


class HodResponse(ORMModel):
    id: int
    employee_id: str
    name: str
    department_id: int
    department_code: str


class AdminResponse(ORMModel):
    id: int
    employee_id: str
    name: str
    status: RecordStatus
