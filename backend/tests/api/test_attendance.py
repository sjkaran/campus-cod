from datetime import date

from tests.conftest import run_attendance_flow


def _create_body(world, **over):
    body = {"subject_id": world.sub_cse, "academic_class_id": world.cls_cse, "date": date.today().isoformat()}
    body.update(over)
    return body


def test_faculty_creates_session_as_draft(client, world, auth):
    r = client.post("/api/attendance/sessions", json=_create_body(world), headers=auth("fac1"))
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["status"] == "DRAFT" and d["subject_code"] == "CS601" and d["faculty_name"] == "fac1"


def test_faculty_cannot_create_session_for_unassigned_class(client, world, auth):
    assert client.post("/api/attendance/sessions", json=_create_body(world), headers=auth("fac2")).status_code == 403
    other = _create_body(world, academic_class_id=world.cls_ece)
    assert client.post("/api/attendance/sessions", json=other, headers=auth("fac1")).status_code == 403


def test_student_cannot_create_session(client, world, auth):
    assert client.post("/api/attendance/sessions", json=_create_body(world), headers=auth("s1")).status_code == 403


def test_status_transitions_are_enforced(client, world, auth):
    h = auth("fac1")
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=h).json()["data"]["id"]
    body = {"records": [{"student_id": "S001", "status": "PRESENT"}]}
    # cannot submit while DRAFT, cannot jump DRAFT -> CLOSED, cannot self-set SUBMITTED
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=body, headers=h).status_code == 409
    assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "CLOSED"}, headers=h).status_code == 409
    assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "SUBMITTED"}, headers=h).status_code == 400
    assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "ACTIVE"}, headers=h).status_code == 200
    assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "ACTIVE"}, headers=h).status_code == 409


def test_faculty_submits_own_session_and_absentees_are_derived(client, world, auth):
    sid = run_attendance_flow(client, auth, world, present=("S001",))
    detail = client.get(f"/api/attendance/sessions/{sid}", headers=auth("fac1")).json()["data"]
    assert detail["status"] == "SUBMITTED" and detail["submitted_at"]
    by_pid = {r["student_public_id"]: r["status"] for r in detail["records"]}
    assert by_pid == {"S001": "PRESENT", "S002": "ABSENT"}  # S002 was on the roster but not reported; S003 is another class


def test_submit_response_shape(client, world, auth):
    h = auth("fac1")
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=h).json()["data"]["id"]
    for st in ("ACTIVE", "CLOSED"):
        client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": st}, headers=h)
    r = client.post(f"/api/attendance/sessions/{sid}/submit", headers=h,
                    json={"records": [{"student_id": "S001", "status": "PRESENT"}, {"student_id": "S002", "status": "ABSENT"}]})
    assert r.json() == {"success": True, "session_id": sid, "status": "SUBMITTED", "total": 2, "present": 1, "absent": 1}


def test_faculty_cannot_submit_another_facultys_session(client, world, auth):
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=auth("fac1")).json()["data"]["id"]
    body = {"records": [{"student_id": "S001", "status": "PRESENT"}]}
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=body, headers=auth("fac2")).status_code == 404
    assert client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "ACTIVE"}, headers=auth("fac2")).status_code == 404
    assert client.get(f"/api/attendance/sessions/{sid}", headers=auth("fac2")).status_code == 404


def test_duplicate_student_in_submission_rejected_and_nothing_persisted(client, world, auth):
    h = auth("fac1")
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=h).json()["data"]["id"]
    for st in ("ACTIVE", "CLOSED"):
        client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": st}, headers=h)
    dup = {"records": [{"student_id": "S001", "status": "PRESENT"}, {"student_id": "S001", "status": "ABSENT"}]}
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=dup, headers=h).status_code == 409
    # transaction rolled back: session still CLOSED, so a corrected submission succeeds
    detail = client.get(f"/api/attendance/sessions/{sid}", headers=h).json()["data"]
    assert detail["status"] == "CLOSED" and detail["records"] == []
    ok = {"records": [{"student_id": "S001", "status": "PRESENT"}]}
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=ok, headers=h).status_code == 200


def test_resubmitting_a_submitted_session_rejected(client, world, auth):
    sid = run_attendance_flow(client, auth, world)
    body = {"records": [{"student_id": "S001", "status": "PRESENT"}]}
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=body, headers=auth("fac1")).status_code == 409


def test_student_from_another_class_rejected(client, world, auth):
    h = auth("fac1")
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=h).json()["data"]["id"]
    for st in ("ACTIVE", "CLOSED"):
        client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": st}, headers=h)
    body = {"records": [{"student_id": "S003", "status": "PRESENT"}]}  # ECE student
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json=body, headers=h).status_code == 400
    assert client.post(f"/api/attendance/sessions/{sid}/submit", json={"records": []}, headers=h).status_code == 422


def test_duplicate_external_session_id_conflicts(client, world, auth):
    h = auth("fac1")
    body = _create_body(world, external_session_id="QR-1")
    assert client.post("/api/attendance/sessions", json=body, headers=h).status_code == 201
    assert client.post("/api/attendance/sessions", json=body, headers=h).status_code == 409


def test_student_retrieves_own_attendance_with_backend_computed_percentage(client, world, auth):
    run_attendance_flow(client, auth, world, present=("S001",))
    run_attendance_flow(client, auth, world, present=("S001", "S002"))
    s1 = client.get("/api/students/me/attendance", headers=auth("s1")).json()["data"]
    assert s1["overall"] == {"total_classes": 2, "present": 2, "absent": 0, "percentage": 100.0}
    assert s1["subjects"][0]["subject_code"] == "CS601"
    s2 = client.get("/api/students/me/attendance", headers=auth("s2")).json()["data"]
    assert s2["overall"] == {"total_classes": 2, "present": 1, "absent": 1, "percentage": 50.0}


def test_student_attendance_is_only_ever_their_own(client, world, auth):
    run_attendance_flow(client, auth, world, present=("S001",))
    # No user-supplied ID exists on this endpoint; s3 (other class) sees nothing of s1's data.
    s3 = client.get("/api/students/me/attendance", headers=auth("s3")).json()["data"]
    assert s3["overall"]["total_classes"] == 0
    assert client.get(f"/api/students/{world.student_pk['s1']}", headers=auth("s3")).status_code == 404


def test_only_submitted_sessions_count(client, world, auth):
    h = auth("fac1")
    sid = client.post("/api/attendance/sessions", json=_create_body(world), headers=h).json()["data"]["id"]
    client.patch(f"/api/attendance/sessions/{sid}/status", json={"status": "ACTIVE"}, headers=h)
    assert client.get("/api/students/me/attendance", headers=auth("s1")).json()["data"]["overall"]["total_classes"] == 0


def test_hod_and_admin_attendance_views_are_scoped(client, world, auth):
    run_attendance_flow(client, auth, world)
    hod = client.get("/api/attendance/department", headers=auth("hod_cse")).json()
    assert hod["pagination"]["total"] == 1 and hod["data"][0]["present"] == 1 and hod["data"][0]["percentage"] == 50.0
    assert client.get("/api/attendance/department", headers=auth("hod_ece")).json()["pagination"]["total"] == 0
    assert client.get("/api/attendance/department", headers=auth("admin")).status_code == 403
    assert client.get("/api/attendance", headers=auth("admin")).json()["pagination"]["total"] == 1
    assert client.get("/api/attendance?department=ECE", headers=auth("admin")).json()["pagination"]["total"] == 0
    assert client.get("/api/attendance", headers=auth("hod_cse")).status_code == 403
    assert client.get("/api/attendance", headers=auth("s1")).status_code == 403


def test_hod_can_view_department_session_detail_but_not_other_departments(client, world, auth):
    sid = run_attendance_flow(client, auth, world)
    assert client.get(f"/api/attendance/sessions/{sid}", headers=auth("hod_cse")).status_code == 200
    assert client.get(f"/api/attendance/sessions/{sid}", headers=auth("hod_ece")).status_code == 404
    assert client.get(f"/api/attendance/sessions/{sid}", headers=auth("s1")).status_code == 403


def test_faculty_my_sessions_lists_only_own(client, world, auth):
    run_attendance_flow(client, auth, world)
    assert client.get("/api/attendance/sessions/my", headers=auth("fac1")).json()["pagination"]["total"] == 1
    assert client.get("/api/attendance/sessions/my", headers=auth("fac2")).json()["pagination"]["total"] == 0


def test_faculty_profile_lists_assignments(client, world, auth):
    d = client.get("/api/faculty/me", headers=auth("fac1")).json()["data"]
    assert d["assignments"][0]["subject"]["code"] == "CS601"
    assert client.get("/api/faculty/me", headers=auth("s1")).status_code == 403
