from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.ops.audit import install_audit_log
from deepresearch.ops.http_boundary import install_http_boundary
from deepresearch.ops.migrations import SCHEMA_VERSION, ensure_schema_version
from deepresearch.ops.readiness import install_readiness
from deepresearch.persistence.store import SQLiteStore


def test_schema_migration_guard_records_current_version(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")

    status = ensure_schema_version(store)
    second = ensure_schema_version(store)

    assert status["schema_version"] == SCHEMA_VERSION
    assert status["current"] is True
    assert second["applied_versions"].count(SCHEMA_VERSION) == 1


def test_readiness_reports_schema_migration_status(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_readiness(app)
    client = TestClient(app)

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["checks"]["schema_migrations"]["status"] == "ok"
    assert payload["checks"]["schema_migrations"]["detail"]["schema_version"] == SCHEMA_VERSION


def test_http_boundary_adds_request_id_and_security_headers(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_http_boundary(app)
    client = TestClient(app)

    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-test"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_http_boundary_rejects_large_requests(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEEPRESEARCH_MAX_BODY_BYTES", "10")
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_http_boundary(app)
    client = TestClient(app)

    response = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME downside", "target": "ACME"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "request body is too large"
    assert response.headers["X-Request-ID"].startswith("req-")


def test_http_boundary_rate_limit_is_optional_but_enforced(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DEEPRESEARCH_RATE_LIMIT_PER_MINUTE", "1")
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_http_boundary(app)
    client = TestClient(app)

    first = client.get("/api/v1/health")
    second = client.get("/api/v1/health")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"] == "rate limit exceeded"


def test_audit_log_persists_runtime_write_events(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_http_boundary(app)
    install_access_control(app)
    install_audit_log(app)
    client = TestClient(app)

    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME durability", "target": "ACME"},
        headers={"X-Request-ID": "req-audit"},
    )
    events = client.get("/api/v1/audit-events").json()

    assert created.status_code == 201
    assert events[0]["request_id"] == "req-audit"
    assert events[0]["action"] == "create_research_case"
    assert events[0]["status_code"] == 201


def test_audit_log_records_actor_for_decision_writes(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    install_audit_log(app)
    client = TestClient(app)
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME governance", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()

    decision = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json={
            "actor": "chair@example.com",
            "action": "APPROVE_THESIS",
            "target_id": run["thesis"]["id"],
            "rationale": "Approved after audit review.",
        },
        headers={"X-Actor": "chair@example.com", "X-Actor-Role": "chair"},
    )
    events = client.get("/api/v1/audit-events?limit=20").json()
    matching = [event for event in events if event["action"] == "record_decision"]

    assert decision.status_code == 200
    assert matching
    assert matching[0]["actor"] == "chair@example.com"
    assert matching[0]["actor_role"] == "chair"
    assert matching[0]["resource_id"] == run_id
