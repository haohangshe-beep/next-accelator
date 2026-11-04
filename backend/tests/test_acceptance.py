"""End-to-end checks for the FTOS MVP acceptance path."""

from __future__ import annotations

from app.seed import DEMO_PASSWORD


def _login(client, email: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": DEMO_PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_track_labels(client) -> None:
    response = client.get("/api/v1/tracks")
    assert response.status_code == 200
    assert response.json() == [
        {"code": "AI", "label": "AI"},
        {"code": "NewSpace", "label": "NewSpace"},
        {"code": "Robotics", "label": "Robotics"},
        {"code": "LowAltitude", "label": "Low Altitude Economy"},
    ]


def test_acceptance_journey(client) -> None:
    bad = client.post("/api/v1/auth/login", json={"email": "learner@demo.ftos", "password": "nope"})
    assert bad.status_code == 401

    learner = _login(client, "learner@demo.ftos")
    navigator = client.get("/api/v1/navigator", headers=learner)
    assert navigator.status_code == 200, navigator.text
    recommendations = navigator.json()["recommendations"]
    assert len(recommendations) >= 3
    for item in recommendations:
        assert item["title"] and item["reason"] and item["action_label"]
        assert item["href"].startswith("/")
    hrefs = [item["href"] for item in recommendations]
    assert "/skills/AI102" in hrefs
    assert "/skills/CV101" in hrefs
    assert any(href.startswith("/missions/") for href in hrefs)

    passport = client.get("/api/v1/passport/alex-chen")
    assert passport.status_code == 200
    body = passport.json()
    assert "learner@demo.ftos" not in passport.text
    assert "email" not in body["profile"]
    assert any(module["code"] == "AI101" for module in body["modules"])
    assert any(mission["title"] == "Port Community Demand Forecast" for mission in body["missions"])
    assert body["certifications"] == []

    low_alt = client.get("/api/v1/missions", params={"track": "LowAltitude", "skill": "DO101"})
    assert low_alt.status_code == 200
    assert len(low_alt.json()) == 1
    assert low_alt.json()[0]["title"] == "Country Park Corridor Survey Plan"

    newspace = client.get("/api/v1/missions", params={"track": "NewSpace", "skill": "PE101"})
    assert len(newspace.json()) == 1
    assert newspace.json()[0]["required_skill_codes"] == ["PE101"]

    none = client.get("/api/v1/missions", params={"track": "Robotics", "skill": "DO101"})
    assert none.json() == []

    unknown = client.get("/api/v1/missions", params={"track": "Space"})
    assert unknown.status_code == 400

    ai_missions = client.get("/api/v1/missions", params={"track": "AI", "skill": "AI101"}, headers=learner)
    titles = {mission["title"] for mission in ai_missions.json()}
    assert "Port Community Demand Forecast" in titles
    assert "SME Grant Narrative Assistant" in titles
    assert "Bilingual Service Triage Brief" in titles

    cubesat = next(mission for mission in client.get("/api/v1/missions", params={"track": "NewSpace"}).json())
    blocked = client.post(f"/api/v1/missions/{cubesat['id']}/join", headers=learner)
    assert blocked.status_code == 400
    assert "PE101" in blocked.json()["detail"]

    module = client.get("/api/v1/modules/AI102", headers=learner).json()
    incomplete = client.post(
        "/api/v1/modules/AI102/complete",
        headers=learner,
        json={"checked": [True] + [False] * (len(module["checklist"]) - 1)},
    )
    assert incomplete.status_code == 400
    completed = client.post(
        "/api/v1/modules/AI102/complete",
        headers=learner,
        json={"checked": [True] * len(module["checklist"])},
    )
    assert completed.status_code == 200, completed.text
    assert completed.json()["already_completed"] is False

    passport = client.get("/api/v1/passport/alex-chen").json()
    assert {module["code"] for module in passport["modules"]} >= {"AI101", "AI102"}

    sme = next(mission for mission in ai_missions.json() if mission["title"] == "SME Grant Narrative Assistant")
    joined = client.post(f"/api/v1/missions/{sme['id']}/join", headers=learner)
    assert joined.status_code == 200, joined.text
    assert joined.json()["membership_status"] == "joined"
    submitted = client.post(
        f"/api/v1/missions/{sme['id']}/submit",
        headers=learner,
        json={
            "deliverable_url": "https://notes.demo.ftos/alex-chen/sme-grant",
            "notes": "Two-page narrative draft with one metric and one stated limit.",
        },
    )
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["status"] == "pending"

    port = next(
        mission
        for mission in client.get("/api/v1/missions", params={"skill": "AI101"}, headers=learner).json()
        if mission["title"] == "Port Community Demand Forecast"
    )
    port_detail = client.get(f"/api/v1/missions/{port['id']}", headers=learner).json()
    submission_id = port_detail["my_submission"]["id"]
    denied = client.post(
        f"/api/v1/submissions/{submission_id}/review",
        headers=learner,
        json={"action": "approve", "competency_tags": ["Demand forecasting"]},
    )
    assert denied.status_code == 403

    employer = _login(client, "employer@demo.ftos")
    home = client.get("/api/v1/dashboard", headers=employer)
    assert home.status_code == 200, home.text
    pending = home.json()["employer"]["pending_reviews"]
    assert any(item["mission_title"] == "Port Community Demand Forecast" for item in pending)
    sme_submission = next(
        item for item in pending if item["mission_title"] == "SME Grant Narrative Assistant"
    )
    changes = client.post(
        f"/api/v1/submissions/{sme_submission['id']}/review",
        headers=employer,
        json={"action": "request_changes", "feedback": "Name the decision the metric changes."},
    )
    assert changes.status_code == 200, changes.text
    assert changes.json()["submission"]["status"] == "changes_requested"

    resubmit = client.post(
        f"/api/v1/missions/{sme['id']}/submit",
        headers=learner,
        json={
            "deliverable_url": "https://notes.demo.ftos/alex-chen/sme-grant-v2",
            "notes": "Revised draft. The metric changes which paragraph the reviewer reads first.",
        },
    )
    assert resubmit.status_code == 200, resubmit.text
    assert resubmit.json()["status"] == "pending"

    approved = client.post(
        f"/api/v1/submissions/{submission_id}/review",
        headers=employer,
        json={"action": "approve", "competency_tags": ["Demand forecasting", "Metric design"]},
    )
    assert approved.status_code == 200, approved.text
    certification = approved.json()["certification"]
    assert "Demand forecasting" in certification["competency_tags"]
    assert "Alex Chen" in certification["statement"]

    public = client.get("/api/v1/passport/alex-chen")
    assert public.status_code == 200
    public_body = public.json()
    assert any(module["code"] == "AI102" for module in public_body["modules"])
    assert any(mission["title"] == "SME Grant Narrative Assistant" for mission in public_body["missions"])
    assert any("Demand forecasting" in cert["competency_tags"] for cert in public_body["certifications"])
    assert "learner@demo.ftos" not in public.text

    admin = _login(client, "admin@demo.ftos")
    created = client.post(
        "/api/v1/admin/modules",
        headers=admin,
        json={
            "code": "AI103",
            "title": "Evaluation Reviews",
            "track": "AI",
            "level": "Advanced",
            "summary": "Run a structured review of someone else's model card and metric.",
            "learning_outcomes": ["Write a review note an author can act on without a meeting."],
            "estimated_hours": 4,
            "prerequisites": ["AI102"],
            "checklist": ["I can separate a metric problem from a writing problem."],
        },
    )
    assert created.status_code == 201, created.text
    deleted = client.delete("/api/v1/admin/modules/AI103", headers=admin)
    assert deleted.status_code == 204

    wait = client.post("/api/v1/waitlist", json={"email": "future@example.com", "topic": "talent"})
    assert wait.status_code == 200
    again = client.post("/api/v1/waitlist", json={"email": "future@example.com", "topic": "talent"})
    assert again.json()["already_registered"] is True
