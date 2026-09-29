def _payload(**over):
    body = {"title": "Exam notice", "message": "Read the notice board", "audience_type": "ALL_STUDENTS"}
    body.update(over)
    return body


def test_admin_can_publish_to_all_students(client, world, auth):
    r = client.post("/api/notifications", json=_payload(priority="URGENT"), headers=auth("admin"))
    assert r.status_code == 201
    assert r.json()["data"]["priority"] == "URGENT" and r.json()["data"]["author_name"] == "Admin One"


def test_hod_can_publish_to_own_department(client, world, auth):
    body = _payload(audience_type="DEPARTMENT", targets=[{"department_code": "CSE"}])
    assert client.post("/api/notifications", json=body, headers=auth("hod_cse")).status_code == 201
    # department is filled in for the HOD when omitted
    body = _payload(audience_type="SEMESTER", targets=[{"semester": 6}])
    r = client.post("/api/notifications", json=body, headers=auth("hod_cse"))
    assert r.status_code == 201 and r.json()["data"]["targets"][0]["department_id"] == world.cse_id


def test_hod_cannot_target_other_department_or_everyone(client, world, auth):
    other = _payload(audience_type="DEPARTMENT", targets=[{"department_code": "ECE"}])
    assert client.post("/api/notifications", json=other, headers=auth("hod_cse")).status_code == 403
    assert client.post("/api/notifications", json=_payload(), headers=auth("hod_cse")).status_code == 403
    single = _payload(audience_type="SPECIFIC_GROUP", targets=[{"student_id": "S003"}])  # ECE student
    assert client.post("/api/notifications", json=single, headers=auth("hod_cse")).status_code == 403


def test_student_and_faculty_cannot_publish(client, world, auth):
    assert client.post("/api/notifications", json=_payload(), headers=auth("s1")).status_code == 403
    assert client.post("/api/notifications", json=_payload(), headers=auth("fac1")).status_code == 403


def test_invalid_audience_definitions_rejected(client, world, auth):
    h = auth("admin")
    assert client.post("/api/notifications", json=_payload(audience_type="DEPARTMENT"), headers=h).status_code == 400
    assert client.post("/api/notifications", json=_payload(targets=[{"semester": 6}]), headers=h).status_code == 400
    bad_section = _payload(audience_type="SECTION", targets=[{"department_code": "CSE", "semester": 6}])
    assert client.post("/api/notifications", json=bad_section, headers=h).status_code == 400
    unknown = _payload(audience_type="DEPARTMENT", targets=[{"department_code": "XYZ"}])
    assert client.post("/api/notifications", json=unknown, headers=h).status_code == 400
    assert client.post("/api/notifications", json=_payload(expires_at="2000-01-01T00:00:00Z"), headers=h).status_code == 400


def test_student_sees_only_relevant_notifications(client, world, auth):
    admin, hod = auth("admin"), auth("hod_cse")
    client.post("/api/notifications", json=_payload(title="For everyone"), headers=admin)
    client.post("/api/notifications", json=_payload(title="CSE only", audience_type="DEPARTMENT", targets=[{"department_code": "CSE"}]), headers=hod)
    client.post("/api/notifications", json=_payload(title="ECE sec A", audience_type="SECTION",
                                                    targets=[{"department_code": "ECE", "semester": 6, "section": "a"}]), headers=admin)
    client.post("/api/notifications", json=_payload(title="Just S002", audience_type="SPECIFIC_GROUP", targets=[{"student_id": "S002"}]), headers=admin)

    titles = lambda user: {n["title"] for n in client.get("/api/notifications", headers=auth(user)).json()["data"]}
    assert titles("s1") == {"For everyone", "CSE only"}
    assert titles("s2") == {"For everyone", "CSE only", "Just S002"}
    assert titles("s3") == {"For everyone", "ECE sec A"}


def test_expired_notifications_are_hidden(client, world, auth, session_factory):
    from datetime import datetime, timedelta, timezone
    import app.models as m
    n_id = client.post("/api/notifications", json=_payload(), headers=auth("admin")).json()["data"]["id"]
    with session_factory() as db:
        db.get(m.Notification, n_id).expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()
    assert client.get("/api/notifications", headers=auth("s1")).json()["pagination"]["total"] == 0


def test_read_state_is_per_student(client, world, auth):
    n_id = client.post("/api/notifications", json=_payload(), headers=auth("admin")).json()["data"]["id"]
    assert client.patch(f"/api/notifications/{n_id}/read", headers=auth("s1")).json()["data"] == {"notification_id": n_id, "is_read": True}
    assert client.patch(f"/api/notifications/{n_id}/read", headers=auth("s1")).status_code == 200  # idempotent
    s1 = client.get("/api/notifications", headers=auth("s1")).json()["data"][0]
    s2 = client.get("/api/notifications", headers=auth("s2")).json()["data"][0]
    assert s1["is_read"] is True and s2["is_read"] is False
    assert client.get("/api/notifications?unread=true", headers=auth("s1")).json()["pagination"]["total"] == 0
    assert client.get("/api/notifications?unread=true", headers=auth("s2")).json()["pagination"]["total"] == 1


def test_student_cannot_mark_invisible_notification_read(client, world, auth):
    body = _payload(audience_type="DEPARTMENT", targets=[{"department_code": "ECE"}])
    n_id = client.post("/api/notifications", json=body, headers=auth("admin")).json()["data"]["id"]
    assert client.patch(f"/api/notifications/{n_id}/read", headers=auth("s1")).status_code == 404


def test_publisher_listings(client, world, auth):
    client.post("/api/notifications", json=_payload(), headers=auth("admin"))
    client.post("/api/notifications", json=_payload(audience_type="DEPARTMENT", targets=[{"department_code": "CSE"}]), headers=auth("hod_cse"))
    assert client.get("/api/notifications/admin", headers=auth("admin")).json()["pagination"]["total"] == 2
    assert client.get("/api/notifications/created-by-me", headers=auth("admin")).json()["pagination"]["total"] == 1
    assert client.get("/api/notifications/created-by-me", headers=auth("hod_cse")).json()["pagination"]["total"] == 1
    assert client.get("/api/notifications/created-by-me", headers=auth("hod_ece")).json()["pagination"]["total"] == 0
    assert client.get("/api/notifications/admin", headers=auth("hod_cse")).status_code == 403
