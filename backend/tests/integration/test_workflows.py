"""End-to-end flows across roles, exactly as the four client apps will drive them."""
from tests.conftest import gatepass_payload


def test_gate_pass_workflow_student_to_hod_and_back(client, world, auth):
    s, hod = auth("s1"), auth("hod_cse")
    created = client.post("/api/gatepasses", json=gatepass_payload(), headers=s).json()["data"]
    assert created["status"] == "PENDING"

    pending = client.get("/api/gatepasses/pending", headers=hod).json()
    assert [g["id"] for g in pending["data"]] == [created["id"]]

    approved = client.patch(f"/api/gatepasses/{created['id']}/approve", json={"remarks": "Safe travels"}, headers=hod)
    assert approved.status_code == 200

    final = client.get(f"/api/gatepasses/{created['id']}", headers=s).json()["data"]
    assert final["status"] == "APPROVED" and final["hod_remarks"] == "Safe travels"
    assert client.get("/api/gatepasses/pending", headers=hod).json()["pagination"]["total"] == 0


def test_attendance_workflow_faculty_to_student_hod_admin(client, world, auth):
    from tests.conftest import run_attendance_flow
    sid = run_attendance_flow(client, auth, world, present=("S001", "S002"), external_id="QR-42")

    assert client.get("/api/students/me/attendance", headers=auth("s1")).json()["data"]["overall"]["percentage"] == 100.0
    assert client.get(f"/api/attendance/sessions/{sid}", headers=auth("hod_cse")).json()["data"]["external_session_id"] == "QR-42"
    assert client.get("/api/analytics/overview", headers=auth("admin")).json()["data"]["attendance"]["present"] == 2
    assert client.get("/api/admin/audit-logs?action=ATTENDANCE_SUBMITTED", headers=auth("admin")).json()["pagination"]["total"] == 1


def test_notification_workflow_admin_to_student(client, world, auth):
    body = {"title": "Holiday declared", "message": "Campus closed Monday", "audience_type": "ALL_STUDENTS", "priority": "IMPORTANT"}
    client.post("/api/notifications", json=body, headers=auth("admin"))
    got = client.get("/api/notifications", headers=auth("s3")).json()["data"]
    assert len(got) == 1 and got[0]["title"] == "Holiday declared" and got[0]["is_read"] is False
    client.patch(f"/api/notifications/{got[0]['id']}/read", headers=auth("s3"))
    assert client.get("/api/notifications?unread=true", headers=auth("s3")).json()["pagination"]["total"] == 0


def test_error_envelope_and_validation_format(client, world, auth):
    r = client.post("/api/auth/login", json={"username": "x"})
    assert r.status_code == 422 and r.json()["detail"].startswith("Validation error") and r.json()["errors"][0]["field"] == "password"
    assert client.get("/api/gatepasses/999999", headers=auth("admin")).json() == {"detail": "Gate pass not found"}
    assert client.get("/health").json() == {"status": "ok"}
