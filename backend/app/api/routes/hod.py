from fastapi import APIRouter, Depends

from app.api.responses import COMMON_ERRORS, ok
from app.core.dependencies import current_hod
from app.models import Hod
from app.schemas.common import DataResponse
from app.schemas.faculty import HodResponse

router = APIRouter(prefix="/hod", tags=["HOD"], responses=COMMON_ERRORS)


@router.get("/me", response_model=DataResponse[HodResponse], summary="Own profile")
def my_profile(hod: Hod = Depends(current_hod)):
    return ok(HodResponse, hod)
