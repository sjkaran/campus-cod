from fastapi import APIRouter, Depends

from app.api.responses import COMMON_ERRORS, ok
from app.core.dependencies import current_faculty
from app.models import Faculty
from app.schemas.common import DataResponse
from app.schemas.faculty import FacultyResponse

router = APIRouter(prefix="/faculty", tags=["Faculty"], responses=COMMON_ERRORS)


@router.get("/me", response_model=DataResponse[FacultyResponse], summary="Own profile with assigned subjects/classes")
def my_profile(faculty: Faculty = Depends(current_faculty)):
    return ok(FacultyResponse, faculty)
