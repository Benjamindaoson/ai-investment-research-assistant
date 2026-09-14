from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore


def test_enqueue_response_contains_frontend_run_control_identity(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME durability", "target": "ACME"})
    run_id = created.json()["run_id"]
    case_id = created.json()["case_id"]

    response = client.post(f"/api/v1/research-runs/{run_id}/enqueue")

    assert response.status_code == 202
    assert response.json() == {"id": run_id, "case_id": case_id, "run_id": run_id, "state": "CREATED", "queued": True}
