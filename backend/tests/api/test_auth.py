from tests.conftest import PASSWORD, login


def test_valid_login_returns_token_and_user_without_password(client, world):
    r = client.post("/api/auth/login", json={"username": "s1", "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer" and body["access_token"]
    assert body["user"]["role"] == "STUDENT" and body["user"]["username"] == "s1"
    assert "password" not in r.text.lower()


def test_wrong_password_is_401(client, world):
    r = client.post("/api/auth/login", json={"username": "s1", "password": "nope"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect username or password"


def test_unknown_user_gets_same_401(client, world):
    r = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Incorrect username or password"


def test_inactive_user_cannot_log_in(client, world):
    r = client.post("/api/auth/login", json={"username": "ghost", "password": PASSWORD})
    assert r.status_code == 403


def test_protected_endpoint_requires_token(client, world):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_returns_current_user(client, world, auth):
    r = client.get("/api/auth/me", headers=auth("hod_cse"))
    assert r.status_code == 200
    assert r.json()["data"]["role"] == "HOD" and r.json()["data"]["department_code"] == "CSE"


def test_token_stops_working_when_user_deactivated(client, world, auth, session_factory):
    headers = auth("s1")
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    import app.models as m
    with session_factory() as db:
        db.query(m.User).filter_by(username="s1").update({"is_active": False})
        db.commit()
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_login_is_written_to_audit_log(client, world, auth):
    login(client, "s1")
    r = client.get("/api/admin/audit-logs?action=LOGIN", headers=auth("admin"))
    assert r.status_code == 200 and r.json()["pagination"]["total"] >= 1
