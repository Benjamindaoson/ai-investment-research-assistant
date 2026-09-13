import sqlite3

from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.planner import DeterministicResearchPlanner, PlannerProviderError


class FailingPlanner:
    name = "llm:failing"
    version = "v1"

    def plan(self, case):
        raise PlannerProviderError("planner provider unavailable")


class InvalidPlanPlanner:
    name = "invalid-planner"
    version = "v1"

    def plan(self, case):
        plan = DeterministicResearchPlanner().plan(case)
        return plan.model_copy(update={"input_hash": "0" * 64})


def test_api_creates_and_executes_case(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's margin durability", "target": "ACME"},
    )
    assert created.status_code == 201
    case = client.get(f"/api/v1/research-cases/{created.json()['case_id']}")
    assert case.status_code == 200
    assert case.json()["id"] == created.json()["case_id"]
    assert case.json()["target"] == "ACME"
    assert case.json()["mandate"] == {
        "decision_type": "INVESTMENT_COMMITTEE",
        "time_horizon": "12 months",
        "materiality": "MEDIUM",
        "required_outputs": ["investment memo"],
        "constraints": [],
    }
    assert "state" not in case.json()
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
    assert [section["section_key"] for section in memo.json()["sections"]] == [
        "thesis", "evidence", "risks", "scenarios", "decision"
    ]

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
    assert client.get("/api/v1/research-cases/missing").status_code == 404


def test_api_persists_explicit_mandate_in_case_and_plan(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    mandate = {
        "decision_type": "DUE_DILIGENCE",
        "time_horizon": "36 months",
        "materiality": "HIGH",
        "required_outputs": ["investment memo", "valuation sensitivity"],
        "constraints": ["Exclude management projections"],
    }

    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME durability before acquisition", "target": "ACME", "mandate": mandate},
    )
    assert created.status_code == 201
    case = client.get(f"/api/v1/research-cases/{created.json()['case_id']}")
    plan = client.get(f"/api/v1/research-runs/{created.json()['run_id']}/plan")

    assert case.json()["mandate"] == mandate
    assert plan.json()["mandate"] == mandate
    assert plan.json()["provenance"]["mandate"] == mandate


def test_api_rejects_blank_mandate_entries(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))

    response = client.post(
        "/api/v1/research-cases",
        json={
            "question": "Assess ACME durability",
            "target": "ACME",
            "mandate": {"required_outputs": ["  "]},
        },
    )

    assert response.status_code == 422


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


def test_api_maps_active_run_lease_to_conflict(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    client = TestClient(create_app(store))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME lease conflict", "target": "ACME"})
    run_id = created.json()["run_id"]
    assert store.acquire_run_lease(run_id, "existing-executor", 60)

    response = client.post(f"/api/v1/research-runs/{run_id}/execute")

    assert response.status_code == 409
    assert response.json()["detail"] == f"research run {run_id} is already being executed"


def test_api_calculates_only_with_qualified_run_evidence(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    evidence_id = run["evidence"][0]["id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120", "prior_revenue": "100"},
            "evidence_ids": {"revenue": [evidence_id], "prior_revenue": [evidence_id]},
        },
    )

    assert response.status_code == 200
    assert response.json()["revenue_growth_pct"] == "20.0"
    assert response.json()["evidence_ids"] == {"revenue": [evidence_id], "prior_revenue": [evidence_id]}
    revenue_entry = next(item for item in response.json()["calculation_ledger"] if item["metric"] == "revenue_growth_pct")
    assert revenue_entry["status"] == "AVAILABLE"
    assert revenue_entry["evidence_ids"] == [evidence_id]
    persisted = client.get(f"/api/v1/research-runs/{run_id}/financial-analysis")
    assert persisted.status_code == 200
    assert persisted.json() == response.json()
    events = client.get(f"/api/v1/research-runs/{run_id}/events").json()
    analysis_event = next(item for item in events if item["event_type"] == "FINANCIAL_ANALYSIS_RECORDED")
    assert analysis_event["payload"]["evidence_ids"] == {"revenue": [evidence_id], "prior_revenue": [evidence_id]}


def test_api_rejects_financial_evidence_not_in_run(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120"},
            "evidence_ids": {"revenue": ["not-in-run"]},
        },
    )

    assert response.status_code == 422
    assert "not found in run" in response.json()["detail"]
    assert client.get(f"/api/v1/research-runs/{run_id}/financial-analysis").status_code == 404


def test_financial_analysis_survives_runtime_reconstruction(tmp_path) -> None:
    store_path = tmp_path / "runtime.sqlite3"
    first_client = TestClient(create_app(SQLiteStore(store_path)))
    created = first_client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]
    evidence_id = first_client.post(f"/api/v1/research-runs/{run_id}/execute").json()["evidence"][0]["id"]
    posted = first_client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120"},
            "evidence_ids": {"revenue": [evidence_id]},
        },
    )

    second_client = TestClient(create_app(SQLiteStore(store_path)))
    restored = second_client.get(f"/api/v1/research-runs/{run_id}/financial-analysis")

    assert posted.status_code == 200
    assert restored.status_code == 200
    assert restored.json() == posted.json()


def test_api_rejects_financial_evidence_that_needs_review(tmp_path) -> None:
    class IncompleteEvidenceProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            return [
                record.model_copy(update={"source_url": None, "locator": None, "content_hash": None})
                for record in super().collect(task, case)
            ]

    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3"), provider=IncompleteEvidenceProvider()))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    evidence_id = run["evidence"][0]["id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120"},
            "evidence_ids": {"revenue": [evidence_id]},
        },
    )

    assert response.status_code == 422
    assert "not qualified" in response.json()["detail"]


def test_api_rejects_unusable_financial_evidence_fields(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]

    response = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120"},
            "evidence_ids": {"revenue": ["evidence-1"], "cash": ["evidence-1"]},
        },
    )

    assert response.status_code == 422
    assert "supplied financial fields" in str(response.json()["detail"])


def test_api_rejects_unknown_or_missing_financial_evidence_links(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME revenue", "target": "ACME"})
    run_id = created.json()["run_id"]

    unknown = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120"},
            "evidence_ids": {"revenue": ["evidence-1"], "ebitda": ["evidence-1"]},
        },
    )
    missing = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {"period": "FY2025", "revenue": "120", "prior_revenue": "100"},
            "evidence_ids": {"revenue": ["evidence-1"]},
        },
    )

    assert unknown.status_code == 422
    assert "unknown financial evidence fields" in str(unknown.json()["detail"])
    assert missing.status_code == 422
    assert "missing evidence links" in str(missing.json()["detail"])


def test_api_records_red_team_review_and_reopens_thesis(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME downside", "target": "ACME"})
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    counter_id = next(item["id"] for item in run["evidence"] if item["stance"] == "COUNTER")

    response = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json={
            "reviewer": "analyst@example.com",
            "challenge": "What if the observed growth signal is not durable?",
            "evidence_ids": [counter_id],
            "outcome": "REQUIRES_RESEARCH",
            "rationale": "The downside evidence requires a focused follow-up.",
        },
    )
    listed = client.get(f"/api/v1/research-runs/{run_id}/red-team-reviews")
    events = client.get(f"/api/v1/research-runs/{run_id}/events").json()

    assert response.status_code == 200
    assert response.json()["thesis"]["review_status"] == "NEEDS_REVIEW"
    assert response.json()["memo"]["status"] == "READY_FOR_REVIEW"
    assert response.json()["red_team_reviews"][0]["evidence_ids"] == [counter_id]
    assert listed.status_code == 200
    assert listed.json() == response.json()["red_team_reviews"]
    assert any(event["event_type"] == "RED_TEAM_REVIEW_RECORDED" for event in events)


def test_api_rejects_supporting_red_team_evidence_without_mutation(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME downside", "target": "ACME"})
    run_id = created.json()["run_id"]
    run = client.post(f"/api/v1/research-runs/{run_id}/execute").json()
    supporting_id = next(item["id"] for item in run["evidence"] if item["stance"] == "SUPPORTING")
    before = client.get(f"/api/v1/research-runs/{run_id}").json()
    events_before = client.get(f"/api/v1/research-runs/{run_id}/events").json()

    response = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json={
            "reviewer": "analyst@example.com",
            "challenge": "Challenge with supporting evidence",
            "evidence_ids": [supporting_id],
            "rationale": "This should be rejected by the stance boundary.",
        },
    )

    assert response.status_code == 422
    assert "counter or conflicting" in response.json()["detail"]
    assert client.get(f"/api/v1/research-runs/{run_id}").json() == before
    assert client.get(f"/api/v1/research-runs/{run_id}/events").json() == events_before
    assert client.get("/api/v1/research-runs/missing/red-team-reviews").status_code == 404


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


def test_api_reads_memory_from_run_without_client_target(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME memory", "target": "ACME"})
    run_id = created.json()["run_id"]
    client.post(f"/api/v1/research-runs/{run_id}/execute")

    by_run = client.get(f"/api/v1/research-runs/{run_id}/memory")
    by_target = client.get("/api/v1/investment-memory/ACME")

    assert by_run.status_code == 200
    assert by_run.json() == by_target.json()
    assert client.get("/api/v1/research-runs/missing/memory").status_code == 404


def test_api_reruns_existing_case_without_overwriting_original(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME rerun", "target": "ACME"})
    case_id = created.json()["case_id"]
    original_id = created.json()["run_id"]
    original = client.get(f"/api/v1/research-runs/{original_id}").json()

    rerun = client.post(f"/api/v1/research-cases/{case_id}/runs")
    original_after = client.get(f"/api/v1/research-runs/{original_id}")

    assert rerun.status_code == 201
    assert rerun.json()["case_id"] == case_id
    assert rerun.json()["run_id"] != original_id
    assert original_after.status_code == 200
    assert original_after.json() == original
    assert client.post("/api/v1/research-cases/missing/runs").status_code == 404
    history = client.get(f"/api/v1/research-cases/{case_id}/runs")
    assert history.status_code == 200
    assert [item["id"] for item in history.json()] == [original_id, rerun.json()["run_id"]]
    assert client.get("/api/v1/research-cases/missing/runs").status_code == 404


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


def test_api_replans_a_partial_run(tmp_path) -> None:
    class EventuallyAvailable(DeterministicEvidenceProvider):
        attempt = 0

        def collect(self, task, case):
            self.attempt += 1
            if self.attempt == 1:
                self.calls.append(task.id)
                return []
            return super().collect(task, case)

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    client = TestClient(create_app(store, provider=EventuallyAvailable()))
    created = client.post("/api/v1/research-cases", json={"question": "Assess ACME risk", "target": "ACME"})
    run_id = created.json()["run_id"]

    partial = client.post(f"/api/v1/research-runs/{run_id}/execute")
    replanned = client.post(f"/api/v1/research-runs/{run_id}/replan")
    completed = client.post(f"/api/v1/research-runs/{run_id}/execute")

    assert partial.json()["state"] == "PARTIAL"
    assert replanned.status_code == 200
    assert replanned.json()["state"] == "CREATED"
    assert replanned.json()["id"] == run_id
    assert completed.json()["state"] == "COMPLETED"
    assert client.post(f"/api/v1/research-runs/{run_id}/replan").status_code == 422
    assert client.post("/api/v1/research-runs/missing/replan").status_code == 404


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


def test_api_maps_planner_provider_failure_without_persisting_case(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    client = TestClient(create_app(store, planner=FailingPlanner()))

    response = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's downside risk", "target": "ACME"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "planner provider unavailable"
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0


def test_api_maps_invalid_plan_without_persisting_case(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    client = TestClient(create_app(store, planner=InvalidPlanPlanner()))

    response = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's downside risk", "target": "ACME"},
    )

    assert response.status_code == 422
    assert "input hash does not match" in response.json()["detail"]
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0


def test_api_uses_canonical_fin_evidence_configuration(monkeypatch, tmp_path) -> None:
    class CapturingHttpProvider:
        last = None

        def __init__(self, base_url, timeout_seconds):
            type(self).last = (base_url, timeout_seconds)

    monkeypatch.setattr("deepresearch.api.HttpEvidenceProvider", CapturingHttpProvider)
    monkeypatch.setenv("FIN_EVIDENCE_BASE_URL", "http://canonical.test")
    monkeypatch.setenv("FIN_EVIDENCE_TIMEOUT_SECONDS", "17")
    monkeypatch.setenv("FINEVIDENCE_BASE_URL", "http://legacy.test")
    monkeypatch.setenv("FINEVIDENCE_TIMEOUT_SECONDS", "31")

    create_app(SQLiteStore(tmp_path / "runtime.sqlite3"), planner=DeterministicResearchPlanner())

    assert CapturingHttpProvider.last == ("http://canonical.test", 17.0)


def test_api_keeps_legacy_fin_evidence_configuration_compatible(monkeypatch, tmp_path) -> None:
    class CapturingHttpProvider:
        last = None

        def __init__(self, base_url, timeout_seconds):
            type(self).last = (base_url, timeout_seconds)

    monkeypatch.setattr("deepresearch.api.HttpEvidenceProvider", CapturingHttpProvider)
    monkeypatch.delenv("FIN_EVIDENCE_BASE_URL", raising=False)
    monkeypatch.delenv("FIN_EVIDENCE_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("FINEVIDENCE_BASE_URL", "http://legacy.test")
    monkeypatch.setenv("FINEVIDENCE_TIMEOUT_SECONDS", "31")

    create_app(SQLiteStore(tmp_path / "runtime.sqlite3"), planner=DeterministicResearchPlanner())

    assert CapturingHttpProvider.last == ("http://legacy.test", 31.0)


def test_api_uses_deterministic_provider_only_without_fin_evidence_url(monkeypatch, tmp_path) -> None:
    class CapturingDeterministicProvider:
        created = False

        def __init__(self):
            type(self).created = True

    monkeypatch.setattr("deepresearch.api.DeterministicEvidenceProvider", CapturingDeterministicProvider)
    monkeypatch.delenv("FIN_EVIDENCE_BASE_URL", raising=False)
    monkeypatch.delenv("FINEVIDENCE_BASE_URL", raising=False)

    create_app(SQLiteStore(tmp_path / "runtime.sqlite3"), planner=DeterministicResearchPlanner())

    assert CapturingDeterministicProvider.created is True
