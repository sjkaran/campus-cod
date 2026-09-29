from tests.conftest import gatepass_payload, run_attendance_flow


def test_overview_admin_and_hod_scopes(client, world, auth):
    run_attendance_flow(client, auth, world, present=("S001",))
    client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1"))
    admin = client.get("/api/analytics/overview", headers=auth("admin")).json()["data"]
    assert admin["scope"] == "INSTITUTION" and admin["students"] == 3 and admin["departments"] == 2
    assert admin["attendance"]["percentage"] == 50.0 and admin["gate_passes"]["pending"] == 1
    hod = client.get("/api/analytics/overview", headers=auth("hod_cse")).json()["data"]
    assert hod["scope"] == "DEPARTMENT" and hod["students"] == 2
    ece = client.get("/api/analytics/overview", headers=auth("hod_ece")).json()["data"]
    assert ece["students"] == 1 and ece["attendance"]["total_classes"] == 0 and ece["gate_passes"]["total"] == 0


def test_faculty_overview_contains_only_their_sessions(client, world, auth):
    run_attendance_flow(client, auth, world)
    fac1 = client.get("/api/analytics/overview", headers=auth("fac1")).json()["data"]
    assert fac1["scope"] == "FACULTY" and fac1["attendance"]["total_classes"] == 2 and fac1["students"] is None
    assert client.get("/api/analytics/overview", headers=auth("fac2")).json()["data"]["attendance"]["total_classes"] == 0


def test_low_attendance_and_group_breakdowns(client, world, auth):
    run_attendance_flow(client, auth, world, present=("S001",))
    a = client.get("/api/analytics/attendance?threshold=75", headers=auth("admin")).json()["data"]
    assert [s["student_id"] for s in a["low_attendance"]] == ["S002"]
    assert a["low_attendance"][0]["summary"]["percentage"] == 0.0
    depts = client.get("/api/analytics/attendance/departments", headers=auth("admin")).json()["data"]
    assert depts[0]["key"] == "CSE" and depts[0]["summary"]["percentage"] == 50.0
    subs = client.get("/api/analytics/attendance/subjects", headers=auth("hod_cse")).json()["data"]
    assert subs[0]["key"] == "CS601"
    assert client.get("/api/analytics/attendance/departments", headers=auth("fac1")).status_code == 403
    assert client.get("/api/analytics/gatepasses", headers=auth("fac1")).status_code == 403


def test_gatepass_analytics_counts(client, world, auth):
    ids = [client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1")).json()["data"]["id"] for _ in range(3)]
    client.patch(f"/api/gatepasses/{ids[0]}/approve", headers=auth("hod_cse"))
    client.patch(f"/api/gatepasses/{ids[1]}/reject", json={"remarks": "not allowed"}, headers=auth("hod_cse"))
    c = client.get("/api/analytics/gatepasses", headers=auth("hod_cse")).json()["data"]
    assert (c["pending"], c["approved"], c["rejected"], c["total"]) == (1, 1, 1, 3)


def test_attendance_report_json_and_csv(client, world, auth):
    run_attendance_flow(client, auth, world, present=("S001",))
    j = client.get("/api/reports/attendance", headers=auth("admin")).json()
    rows = {r["student_id"]: r for r in j["data"]}
    assert rows["S001"]["percentage"] == 100.0 and rows["S002"]["percentage"] == 0.0
    csv = client.get("/api/reports/attendance?format=csv", headers=auth("hod_cse"))
    assert csv.headers["content-type"].startswith("text/csv")
    lines = csv.text.strip().splitlines()
    assert lines[0].startswith("student_id,") and len(lines) == 3
    assert client.get("/api/reports/attendance?department=ECE", headers=auth("hod_cse")).status_code == 403
    assert client.get("/api/reports/attendance", headers=auth("s1")).status_code == 403


def test_students_and_gatepass_reports(client, world, auth):
    client.post("/api/gatepasses", json=gatepass_payload(), headers=auth("s1"))
    assert client.get("/api/reports/students?semester=6", headers=auth("admin")).json()["pagination"]["total"] == 3
    assert client.get("/api/reports/students", headers=auth("hod_cse")).json()["pagination"]["total"] == 2
    assert client.get("/api/reports/students", headers=auth("fac1")).status_code == 403
    gp = client.get("/api/reports/gatepasses?status=PENDING", headers=auth("admin")).json()
    assert gp["pagination"]["total"] == 1 and gp["data"][0]["student_id"] == "S001"
    assert client.get("/api/reports/gatepasses", headers=auth("hod_ece")).json()["pagination"]["total"] == 0
