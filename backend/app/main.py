import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging

log = logging.getLogger("app")

DESCRIPTION = """
Central backend for the Smart Campus Management System (modular monolith).

**Auth:** `POST /api/auth/login` -> use the returned token as `Authorization: Bearer <token>`.
Click **Authorize** above to try endpoints from this page.

**Envelope:** resources are `{"data": ...}`; collections add `{"pagination": {page, page_size, total}}`;
errors are `{"detail": "..."}`.
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    log.info("startup environment=%s", settings.environment)
    yield
    log.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="1.0.0", description=DESCRIPTION, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,  # explicit list from env, never "*"
        allow_credentials=False,                  # bearer tokens, not cookies
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "message": e["msg"]}
            for e in exc.errors()
        ]
        summary = "; ".join(f"{e['field']}: {e['message']}" for e in errors)
        return JSONResponse({"detail": f"Validation error: {summary}", "errors": errors}, status_code=422)

    @app.exception_handler(IntegrityError)
    async def integrity_handler(_: Request, exc: IntegrityError):
        log.warning("integrity_error %s", exc.__class__.__name__, exc_info=exc)
        return JSONResponse({"detail": "The request conflicts with existing data"}, status_code=409)

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(_: Request, exc: SQLAlchemyError):
        log.error("database_error", exc_info=exc)  # details stay in server logs only
        return JSONResponse({"detail": "A database error occurred"}, status_code=500)

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception):
        log.error("unhandled_exception", exc_info=exc)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    @app.get("/health", tags=["System"], summary="Liveness probe")
    def health():
        return {"status": "ok"}

    app.include_router(api_router)
    return app


app = create_app()
