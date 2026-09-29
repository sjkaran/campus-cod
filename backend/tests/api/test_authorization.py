from tests.conftest import gatepass_payload


def test_student_cannot_reach_admin_endpoints(client, world, auth):
    h = auth("s1")
    assert client.get("/api/admin/audit-logs", headers=h).status_code == 403
    assert client.get("/api/students", headers=h).status_code == 403
    assert client.get("/api/analytics/overview", headers=h).status_code == 403
    assert client.post("/api/notifications", headers=h, json={"title": "x y z", "message": "m", "audience_type": "ALL_STUDENTS"}).status_code == 403


def test_student_cannot_approve_gatepass(client, world, auth):
    gp = client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]
    assert client.patch(f"/api/gatepasses/{gp['id']}/approve", headers=auth("s1")).status_code == 403


def test_faculty_cannot_approve_gatepass(client, world, auth):
    gp = client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]
    assert client.patch(f"/api/gatepasses/{gp['id']}/approve", headers=auth("fac1")).status_code == 403


def test_admin_cannot_approve_gatepass(client, world, auth):
    """Admin and HOD are distinct roles: hiding the button in the UI is not the control, this is."""
    gp = client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]
    assert client.patch(f"/api/gatepasses/{gp['id']}/approve", headers=auth("admin")).status_code == 403


def test_hod_cannot_review_other_departments_gatepass(client, world, auth):
    gp = client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]  # CSE student
    r = client.patch(f"/api/gatepasses/{gp['id']}/approve", headers=auth("hod_ece"))
    assert r.status_code == 404  # invisible to other departments
    assert client.get(f"/api/gatepasses/{gp['id']}", headers=auth("hod_ece")).status_code == 404
    pending = client.get("/api/gatepasses/pending", headers=auth("hod_ece")).json()
    assert pending["pagination"]["total"] == 0


def test_hod_cannot_widen_scope_with_department_parameter(client, world, auth):
    h = auth("hod_cse")
    assert client.get("/api/analytics/overview?department=ECE", headers=h).status_code == 403
    assert client.get("/api/analytics/overview?department=CSE", headers=h).status_code == 200
    assert client.get("/api/students?department=ECE", headers=h).status_code == 403
    assert client.get("/api/reports/students?department=ECE", headers=h).status_code == 403
    assert client.get("/api/gatepasses?department=ECE", headers=h).status_code == 403


def test_hod_student_list_is_pinned_to_own_department(client, world, auth):
    r = client.get("/api/students", headers=auth("hod_cse")).json()
    assert r["pagination"]["total"] == 2
    assert {s["department_code"] for s in r["data"]} == {"CSE"}


def test_admin_can_access_system_level_endpoints(client, world, auth):
    h = auth("admin")
    assert client.get("/api/students", headers=h).json()["pagination"]["total"] == 3
    assert client.get("/api/analytics/overview", headers=h).status_code == 200
    assert client.get("/api/analytics/overview?department=ECE", headers=h).status_code == 200
    assert client.get("/api/gatepasses", headers=h).status_code == 200
    assert client.get("/api/reports/students", headers=h).status_code == 200


def test_student_cannot_read_another_students_record(client, world, auth):
    other = world.student_pk["s2"]
    assert client.get(f"/api/students/{other}", headers=auth("s1")).status_code == 404
    assert client.get(f"/api/students/{world.student_pk['s1']}", headers=auth("s1")).status_code == 200


def test_student_cannot_read_another_students_gatepass(client, world, auth):
    gp = client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]
    assert client.get(f"/api/gatepasses/{gp['id']}", headers=auth("s2")).status_code == 404
    assert client.get(f"/api/gatepasses/{gp['id']}", headers=auth("s1")).status_code == 200


def test_pagination_limits_are_enforced(client, world, auth):
    assert client.get("/api/students?page_size=1000", headers=auth("admin")).status_code == 422
    assert client.get("/api/students?page=0", headers=auth("admin")).status_code == 422
