from fastapi import APIRouter

from app.api.routes import (
    admin, analytics, attendance, auth, catalog, faculty, gatepass, hod, notifications, reports, students,
)

api_router = APIRouter(prefix="/api")
for module in (auth, students, faculty, hod, admin, catalog, attendance, gatepass, notifications, analytics, reports):
    api_router.include_router(module.router)
