from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models import User
from app.schemas.auth import LoginRequest, LoginResponse, UserBrief
from app.schemas.common import DataResponse, ErrorResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login", response_model=LoginResponse,
    responses={401: {"model": ErrorResponse, "description": "Incorrect username or password"},
               403: {"model": ErrorResponse, "description": "Account disabled"}},
    summary="Log in and receive a JWT access token",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, body.username, body.password)


@router.get("/me", response_model=DataResponse[UserBrief], responses=COMMON_ERRORS, summary="Current user")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"data": auth_service.user_brief(db, user)}
