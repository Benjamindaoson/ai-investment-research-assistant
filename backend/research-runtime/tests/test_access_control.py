from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.ops.readiness import install_readiness
from deepresearch.persistence.store import SQLiteStore


def _completed_run(client: TestClient) -> tuple[str, dict]:
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME governance", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    return run_id, run


def _counter_evidence_id(run: dict) -> str:
    return next(
        item["id"]
        for item in run["evidence"]
        if item["stance"] == "COUNTER" and item["qualification"] == "QUALIFIED"
    )


def _review_payload(evidence_id: str, reviewer: str = "reviewer@example.com") -> dict:
    return {
        "reviewer": reviewer,
        "challenge": "The thesis may underweight downside evidence.",
        "evidence_ids": [evidence_id],
        "outcome": "SUPPORTED",
        "rationale": "The cited evidence raises a material challenge.",
    }


def _decision_payload(thesis_id: str, actor: str = "chair@example.com") -> dict:
    return {
        "actor": actor,
        "action": "APPROVE_THESIS",
        "target_id": thesis_id,
        "rationale": "Approved after human review.",
    }


def test_configured_api_key_protects_non_health_routes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEEPRESEARCH_API_KEYS", "local-dev-key,backup-key")
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    install_readiness(app)
    client = TestClient(app)

    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/ready").status_code == 200
    assert client.get("/api/v1/research-cases").status_code == 401
    assert client.get("/api/v1/research-cases", headers={"X-API-Key": "wrong"}).status_code == 403
    assert client.get("/api/v1/research-cases", headers={"X-API-Key": "local-dev-key"}).status_code == 200


def test_review_write_requires_actor_headers(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    evidence_id = _counter_evidence_id(run)

    response = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json=_review_payload(evidence_id),
    )

    assert response.status_code == 401
    assert "X-Actor" in response.json()["detail"]


def test_reviewer_can_write_review_but_not_decision(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    evidence_id = _counter_evidence_id(run)
    thesis_id = run["thesis"]["id"]
    reviewer_headers = {"X-Actor": "reviewer@example.com", "X-Actor-Role": "reviewer"}

    review = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json=_review_payload(evidence_id),
        headers=reviewer_headers,
    )
    decision = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json=_decision_payload(thesis_id, actor="reviewer@example.com"),
        headers=reviewer_headers,
    )

    assert review.status_code == 200
    assert decision.status_code == 403
    assert "not allowed" in decision.json()["detail"]


def test_reviewer_body_identity_must_match_actor_header(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    evidence_id = _counter_evidence_id(run)

    response = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json=_review_payload(evidence_id, reviewer="someone-else@example.com"),
        headers={"X-Actor": "reviewer@example.com", "X-Actor-Role": "reviewer"},
    )

    assert response.status_code == 403
    assert "reviewer" in response.json()["detail"]
    assert "X-Actor" in response.json()["detail"]


def test_chair_can_write_decision(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    thesis_id = run["thesis"]["id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json=_decision_payload(thesis_id),
        headers={"X-Actor": "chair@example.com", "X-Actor-Role": "chair"},
    )

    assert response.status_code == 200
    assert response.json()["decisions"][-1]["actor"] == "chair@example.com"


def test_decision_body_identity_must_match_actor_header(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    thesis_id = run["thesis"]["id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json=_decision_payload(thesis_id, actor="other-chair@example.com"),
        headers={"X-Actor": "chair@example.com", "X-Actor-Role": "chair"},
    )

    assert response.status_code == 403
    assert "actor" in response.json()["detail"]
    assert "X-Actor" in response.json()["detail"]
