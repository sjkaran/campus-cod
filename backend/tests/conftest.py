"""Test harness: in-memory SQLite, one fresh database per test, real auth flow (no auth mocking)."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-test-secret-key-0123456789")
os.environ.setdefault("ENVIRONMENT", "test")

from datetime import date, timedelta  # noqa: E402
from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models as m  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.database import get_db  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "Passw0rd!test"
_HASH = hash_password(PASSWORD)  # hash once; Argon2 is deliberately slow


@pytest.fixture()
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")  # make SQLite enforce FKs like PostgreSQL

    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _user(db, username, role, active=True):
    u = m.User(username=username, password_hash=_HASH, role=role, is_active=active)
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def world(session_factory):
    """CSE + ECE, one class each, users for every role.

    admin | hod_cse hod_ece | fac1 (assigned to CSE class) fac2 (no assignments) |
    s1 s2 (CSE 6-A) s3 (ECE 6-A) | ghost (inactive)
    """
    with session_factory() as db:
        cse = m.Department(code="CSE", name="Computer Science")
        ece = m.Department(code="ECE", name="Electronics")
        db.add_all([cse, ece])
        db.flush()
        sub_cse = m.Subject(code="CS601", name="Compilers", department_id=cse.id)
        sub_ece = m.Subject(code="EC601", name="VLSI", department_id=ece.id)
        cls_cse = m.AcademicClass(department_id=cse.id, semester=6, section="A", academic_year="2026-27")
        cls_ece = m.AcademicClass(department_id=ece.id, semester=6, section="A", academic_year="2026-27")
        db.add_all([sub_cse, sub_ece, cls_cse, cls_ece])
        db.flush()

        a = _user(db, "admin", m.Role.ADMIN)
        db.add(m.Admin(user_id=a.id, employee_id="A1", name="Admin One"))
        hods = {}
        for dept, uname in ((cse, "hod_cse"), (ece, "hod_ece")):
            u = _user(db, uname, m.Role.HOD)
            hods[uname] = m.Hod(user_id=u.id, employee_id=uname.upper(), name=uname, department_id=dept.id)
            db.add(hods[uname])
        facs = {}
        for uname, fid in (("fac1", "F1"), ("fac2", "F2")):
            u = _user(db, uname, m.Role.FACULTY)
            facs[uname] = m.Faculty(user_id=u.id, faculty_id=fid, name=uname, email=f"{uname}@x.test", department_id=cse.id)
            db.add(facs[uname])
        db.flush()
        db.add(m.FacultyAssignment(faculty_id=facs["fac1"].id, subject_id=sub_cse.id, academic_class_id=cls_cse.id))

        studs = {}
        for uname, sid, dept in (("s1", "S001", cse), ("s2", "S002", cse), ("s3", "S003", ece)):
            u = _user(db, uname, m.Role.STUDENT)
            studs[uname] = m.Student(
                user_id=u.id, student_id=sid, roll_number=f"R{sid}", name=f"Student {uname}",
                email=f"{uname}@x.test", department_id=dept.id, semester=6, section="A",
            )
            db.add(studs[uname])
        _user(db, "ghost", m.Role.STUDENT, active=False)
        db.commit()

        return SimpleNamespace(
            cse_id=cse.id, ece_id=ece.id, sub_cse=sub_cse.id, cls_cse=cls_cse.id, cls_ece=cls_ece.id,
            student_pk={k: v.id for k, v in studs.items()}, student_pid={k: v.student_id for k, v in studs.items()},
            fac1=facs["fac1"].id, fac2=facs["fac2"].id,
        )


def login(client, username, password=PASSWORD):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth(client, world):
    """auth('s1') -> Authorization headers for that seeded user."""
    cache = {}

    def _get(username):
        if username not in cache:
            cache[username] = login(client, username)
        return cache[username]

    return _get


def gatepass_payload(**over):
    day = date.today() + timedelta(days=2)
    body = {
        "destination": "Home", "reason": "Family function",
        "departure_date": day.isoformat(), "departure_time": "10:00:00",
        "return_date": (day + timedelta(days=1)).isoformat(), "return_time": "18:00:00",
    }
    body.update(over)
    return body


def run_attendance_flow(client, auth, world, present=("S001",), external_id=None):
    """fac1 creates -> activates -> closes -> submits a session. Returns the session id."""
    h = auth("fac1")
    body = {"subject_id": world.sub_cse, "academic_class_id": world.cls_cse, "date": date.today().isoformat()}
    if external_id:
        body["external_session_id"] = external_id
    sid = client.post("/api/attendance/sessions", json=body, headers=h).json()["data"]["id"]
    for st in ("ACTIVE", "CLOSED"):
        assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": st}, headers=h).status_code == 200
    r = client.post(
        f"/api/attendance/sessions/{sid}/submit", headers=h,
        json={"records": [{"student_id": p, "status": "PRESENT"} for p in present]},
    )
    assert r.status_code == 200, r.text
    return sid
