from fastapi import FastAPI
from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.ops.readiness import install_readiness, readiness_snapshot
from deepresearch.persistence.store import SQLiteStore


def test_readiness_reports_ready_runtime(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_readiness(app)
    client = TestClient(app)

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["store"]["status"] == "ok"
    assert payload["checks"]["queue"]["detail"] == "database-scan"
    assert payload["checks"]["tools"]["status"] == "ok"
    assert payload["checks"]["reliability_layer"]["status"] == "ok"


def test_readiness_fails_when_engine_is_missing() -> None:
    app = FastAPI()

    status_code, payload = readiness_snapshot(app)

    assert status_code == 503
    assert payload["status"] == "not_ready"
    assert payload["checks"]["engine"]["status"] == "failed"
