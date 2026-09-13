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

    plan = client.get(f"/api/v1/research-runs/{run_id}/plan")
    assert plan.status_code == 200
    assert plan.json()["status"] == "VALIDATED"
    assert plan.json()["planner_name"] == "deterministic-financial-planner"

    executed = client.post(f"/api/v1/research-runs/{run_id}/execute")
    assert executed.status_code == 200
    assert executed.json()["state"] == "COMPLETED"
    thesis_id = executed.json()["thesis"]["id"]

    memo = client.get(f"/api/v1/research-runs/{run_id}/memo")
    assert memo.status_code == 200
    assert memo.json()["status"] == "READY_FOR_REVIEW"
    assert memo.json()["unresolved_requirement_ids"] == []
    assert len(memo.json()["evidence_ids"]) == 3
    assert len(memo.json()["counter_evidence_ids"]) == 3

    approved = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json={
            "actor": "analyst@example.com",
            "action": "APPROVE_THESIS",
            "target_id": thesis_id,
            "rationale": "Reviewed the linked evidence and assumptions.",
        },
    )
    assert approved.status_code == 200
    assert approved.json()["memo"]["status"] == "APPROVED"

    events = client.get(f"/api/v1/research-runs/{run_id}/events")
    assert events.status_code == 200
    assert any(item["event_type"] == "RUN_COMPLETED" for item in events.json())

    trace = client.get(f"/api/v1/research-runs/{run_id}/trace")
    assert trace.status_code == 200
    assert trace.json()["evidence"]["provenance_complete"] == 6
    assert all(not claim["unresolved_evidence_ids"] for claim in trace.json()["claims"])
    assert client.get("/api/v1/research-runs/missing/trace").status_code == 404
    assert client.get("/api/v1/research-runs/missing/memo").status_code == 404


def test_api_calculates_financial_snapshot(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))

    response = client.post(
        "/api/v1/financial-analysis",
        json={
            "period": "FY2025",
            "revenue": "120",
            "prior_revenue": "100",
            "gross_profit": "60",
            "operating_income": "30",
            "operating_cash_flow": "35",
            "capex": "10",
            "cash": "50",
            "debt": "20",
        },
    )

    assert response.status_code == 200
    assert response.json()["gross_margin_pct"] == "50.0"
    assert response.json()["free_cash_flow"] == "25"
    assert response.json()["unavailable_metrics"] == []


def test_api_reads_target_investment_memory(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created_ids = []
    for question in ("Assess ACME margins", "Reassess ACME margins"):
        created = client.post("/api/v1/research-cases", json={"question": question, "target": "ACME"})
        run_id = created.json()["run_id"]
        client.post(f"/api/v1/research-runs/{run_id}/execute")
        created_ids.append(run_id)

    memory = client.get("/api/v1/investment-memory/ACME")

    assert memory.status_code == 200
    assert memory.json()["run_ids"] == created_ids
    assert memory.json()["latest_run_id"] == created_ids[-1]


def test_api_cancels_run_and_prevents_execution(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME risk", "target": "ACME"})
    run_id = created.json()["run_id"]

    cancelled = client.post(f"/api/v1/research-runs/{run_id}/cancel", json={"reason": "Analyst stopped the run"})
    executed = client.post(f"/api/v1/research-runs/{run_id}/execute")

    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "CANCELLED"
    assert executed.status_code == 200
    assert executed.json()["state"] == "CANCELLED"


def test_api_allows_only_configured_local_cors_origin(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RESEARCH_RUNTIME_CORS_ORIGINS", "http://localhost:3000")
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))

    allowed = client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    denied = client.options(
        "/api/v1/health",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers
