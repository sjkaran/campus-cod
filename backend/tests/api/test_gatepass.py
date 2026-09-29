from datetime import date, timedelta

from tests.conftest import gatepass_payload


def _create(client, auth, **over):
    return client.post("/api/gatepasses", json=gatepass_payload(**over), headers=auth("s1"))


def test_student_creates_request_as_pending(client, world, auth):
    r = _create(client, auth)
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["status"] == "PENDING" and d["hod_id"] is None and d["reviewed_at"] is None
    assert d["student_public_id"] == "S001" and d["department_code"] == "CSE"


def test_student_cannot_set_backend_controlled_fields(client, world, auth):
    r = _create(client, auth, status="APPROVED", hod_id=1)
    assert r.status_code == 422  # extra fields are forbidden


def test_return_before_departure_rejected(client, world, auth):
    day = date.today() + timedelta(days=3)
    r = _create(client, auth, departure_date=day.isoformat(), return_date=(day - timedelta(days=1)).isoformat())
    assert r.status_code == 400


def test_departure_in_the_past_rejected(client, world, auth):
    past = date.today() - timedelta(days=2)
    assert _create(client, auth, departure_date=past.isoformat(), return_date=date.today().isoformat()).status_code == 400


def test_missing_and_short_fields_rejected(client, world, auth):
    assert _create(client, auth, destination="").status_code == 422
    assert _create(client, auth, reason="no").status_code == 422
    body = gatepass_payload()
    body.pop("return_time")
    assert client.post("/api/gatepasses", json=body, headers=auth("s1")).status_code == 422


def test_hod_approves(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    r = client.patch(f"/api/gatepasses/{gp_id}/approve", headers=auth("hod_cse"))
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["status"] == "APPROVED" and d["hod_name"] == "hod_cse" and d["reviewed_at"] is not None


def test_hod_rejects_with_reason(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    r = client.patch(f"/api/gatepasses/{gp_id}/reject", json={"remarks": "Exams next week"}, headers=auth("hod_cse"))
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["status"] == "REJECTED" and d["hod_remarks"] == "Exams next week"


def test_rejection_requires_a_reason(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    h = auth("hod_cse")
    assert client.patch(f"/api/gatepasses/{gp_id}/reject", headers=h).status_code == 422
    assert client.patch(f"/api/gatepasses/{gp_id}/reject", json={}, headers=h).status_code == 422
    assert client.patch(f"/api/gatepasses/{gp_id}/reject", json={"remarks": "   "}, headers=h).status_code == 422
    # still pending afterwards
    assert client.get(f"/api/gatepasses/{gp_id}", headers=auth("s1")).json()["data"]["status"] == "PENDING"


def test_already_reviewed_cannot_be_reviewed_again(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    h = auth("hod_cse")
    assert client.patch(f"/api/gatepasses/{gp_id}/approve", headers=h).status_code == 200
    again = client.patch(f"/api/gatepasses/{gp_id}/reject", json={"remarks": "changed my mind"}, headers=h)
    assert again.status_code == 409
    assert again.json()["detail"] == "Gate pass has already been reviewed."
    assert client.patch(f"/api/gatepasses/{gp_id}/approve", headers=h).status_code == 409


def test_pending_list_and_my_list_and_status_filter(client, world, auth):
    ids = [_create(client, auth).json()["data"]["id"] for _ in range(3)]
    client.patch(f"/api/gatepasses/{ids[0]}/approve", headers=auth("hod_cse"))
    pending = client.get("/api/gatepasses/pending", headers=auth("hod_cse")).json()
    assert pending["pagination"]["total"] == 2
    mine = client.get("/api/gatepasses/my", headers=auth("s1")).json()
    assert mine["pagination"]["total"] == 3
    approved = client.get("/api/gatepasses/my?status=APPROVED", headers=auth("s1")).json()
    assert [g["id"] for g in approved["data"]] == [ids[0]]
    assert client.get("/api/gatepasses/my", headers=auth("s2")).json()["pagination"]["total"] == 0


def test_student_can_cancel_only_pending(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    assert client.patch(f"/api/gatepasses/{gp_id}/cancel", headers=auth("s2")).status_code == 404
    assert client.patch(f"/api/gatepasses/{gp_id}/cancel", headers=auth("s1")).json()["data"]["status"] == "CANCELLED"
    assert client.patch(f"/api/gatepasses/{gp_id}/approve", headers=auth("hod_cse")).status_code == 409


def test_review_is_audited(client, world, auth):
    gp_id = _create(client, auth).json()["data"]["id"]
    client.patch(f"/api/gatepasses/{gp_id}/approve", headers=auth("hod_cse"))
    logs = client.get("/api/admin/audit-logs?action=GATEPASS_APPROVED", headers=auth("admin")).json()
    assert logs["pagination"]["total"] == 1 and logs["data"][0]["resource_id"] == str(gp_id)
