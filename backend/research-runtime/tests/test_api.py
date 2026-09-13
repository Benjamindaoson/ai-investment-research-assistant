from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore


def test_api_creates_and_executes_case(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's margin durability", "target": "ACME"},
    )
    assert created.status_code == 201
    run_id = created.json()["run_id"]

    executed = client.post(f"/api/v1/research-runs/{run_id}/execute")
    assert executed.status_code == 200
    assert executed.json()["state"] == "COMPLETED"

    events = client.get(f"/api/v1/research-runs/{run_id}/events")
    assert events.status_code == 200
    assert any(item["event_type"] == "RUN_COMPLETED" for item in events.json())

    trace = client.get(f"/api/v1/research-runs/{run_id}/trace")
    assert trace.status_code == 200
    assert trace.json()["evidence"]["provenance_complete"] == 6
    assert all(not claim["unresolved_evidence_ids"] for claim in trace.json()["claims"])
    assert client.get("/api/v1/research-runs/missing/trace").status_code == 404
