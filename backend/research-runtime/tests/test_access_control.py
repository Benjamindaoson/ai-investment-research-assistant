from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.persistence.store import SQLiteStore


def _completed_run(client: TestClient) -> tuple[str, dict]:
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME governance", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    return run_id, run


def _review_payload(evidence_id: str) -> dict:
    return {
        "reviewer": "reviewer@example.com",
        "challenge": "The thesis may underweight downside evidence.",
        "evidence_ids": [evidence_id],
        "outcome": "SUPPORTED",
        "rationale": "The cited evidence raises a material challenge.",
    }


def _decision_payload(thesis_id: str) -> dict:
    return {
        "actor": "chair@example.com",
        "action": "APPROVE_THESIS",
        "target_id": thesis_id,
        "rationale": "Approved after human review.",
    }


def test_review_write_requires_actor_headers(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)
    run_id, run = _completed_run(client)
    evidence_id = run["evidence"][0]["id"]

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
    evidence_id = run["evidence"][0]["id"]
    thesis_id = run["thesis"]["id"]
    reviewer_headers = {"X-Actor": "reviewer@example.com", "X-Actor-Role": "reviewer"}

    review = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json=_review_payload(evidence_id),
        headers=reviewer_headers,
    )
    decision = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json=_decision_payload(thesis_id),
        headers=reviewer_headers,
    )

    assert review.status_code == 200
    assert decision.status_code == 403
    assert "not allowed" in decision.json()["detail"]


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
