from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.persistence.store import SQLiteStore


def _supporting_evidence_id(run: dict[str, Any]) -> str:
    return next(
        item["id"]
        for item in run["evidence"]
        if item["stance"] == "SUPPORTING" and item["qualification"] == "QUALIFIED"
    )


def _counter_evidence_id(run: dict[str, Any]) -> str:
    return next(
        item["id"]
        for item in run["evidence"]
        if item["stance"] == "COUNTER" and item["qualification"] == "QUALIFIED"
    )


def _scenario(name: str, revenue_growth: str, margin: str, fcf_margin: str, evidence_id: str) -> dict[str, Any]:
    links = {
        "revenue_growth_pct": [evidence_id],
        "operating_margin_pct": [evidence_id],
        "fcf_margin_pct": [evidence_id],
        "discount_rate_pct": [evidence_id],
        "terminal_growth_pct": [evidence_id],
        "net_cash": [evidence_id],
        "shares_outstanding": [evidence_id],
    }
    return {
        "name": name,
        "revenue_growth_pct": revenue_growth,
        "operating_margin_pct": margin,
        "fcf_margin_pct": fcf_margin,
        "discount_rate_pct": "10",
        "terminal_growth_pct": "3",
        "net_cash": "10",
        "shares_outstanding": "100",
        "evidence_ids": links,
    }


def test_full_workflow_from_case_creation_to_memo_and_decision(tmp_path) -> None:
    app = create_app(SQLiteStore(tmp_path / "runtime.sqlite3"))
    install_access_control(app)
    client = TestClient(app)

    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's margin durability and downside risk", "target": "ACME"},
    )
    assert created.status_code in {200, 201}, created.text
    run_id = created.json()["run_id"]

    executed = client.post(f"/api/v1/research-runs/{run_id}/execute")
    assert executed.status_code == 200, executed.text
    run = executed.json()
    assert run["state"] == "COMPLETED"
    assert run["memo"] is not None
    assert run["thesis"] is not None

    supporting_id = _supporting_evidence_id(run)
    counter_id = _counter_evidence_id(run)
    thesis_id = run["thesis"]["id"]

    financial = client.post(
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        json={
            "snapshot": {
                "period": "FY2025",
                "revenue": "120",
                "prior_revenue": "100",
                "operating_income": "24",
                "operating_cash_flow": "20",
                "capex": "5",
                "cash": "30",
                "debt": "20",
            },
            "evidence_ids": {
                "revenue": [supporting_id],
                "prior_revenue": [supporting_id],
                "operating_income": [supporting_id],
                "operating_cash_flow": [supporting_id],
                "capex": [supporting_id],
                "cash": [supporting_id],
                "debt": [supporting_id],
            },
        },
    )
    assert financial.status_code == 200, financial.text
    assert financial.json()["revenue_growth_pct"] == "20.0"

    valuation = client.post(
        f"/api/v1/research-runs/{run_id}/valuation-scenarios",
        json={
            "base_revenue": "120",
            "base_revenue_evidence_ids": [supporting_id],
            "scenarios": [
                _scenario("BULL", "15", "25", "20", supporting_id),
                _scenario("BASE", "8", "20", "15", supporting_id),
                _scenario("BEAR", "0", "12", "8", supporting_id),
            ],
        },
    )
    assert valuation.status_code == 200, valuation.text
    assert len(valuation.json()["scenarios"]) == 3

    reviewer_headers = {"X-Actor": "reviewer@example.com", "X-Actor-Role": "reviewer"}
    red_team = client.post(
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        json={
            "reviewer": "reviewer@example.com",
            "challenge": "The thesis may underweight qualified downside evidence.",
            "evidence_ids": [counter_id],
            "outcome": "SUPPORTED",
            "rationale": "The counter-evidence is material enough to track in the final memo.",
        },
        headers=reviewer_headers,
    )
    assert red_team.status_code == 200, red_team.text
    assert red_team.json()["red_team_reviews"][-1]["reviewer"] == "reviewer@example.com"

    for role in ("BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER"):
        ic = client.post(
            f"/api/v1/research-runs/{run_id}/ic-reviews",
            json={
                "role": role,
                "reviewer": "reviewer@example.com",
                "position": "SUPPORTIVE" if role == "BULL" else "MIXED",
                "recommendation": "APPROVE" if role == "BULL" else "HOLD",
                "rationale": f"The {role.lower()} review considered the evidence package before decisioning.",
                "evidence_ids": [supporting_id],
            },
            headers=reviewer_headers,
        )
        assert ic.status_code == 200, ic.text

    chair_headers = {"X-Actor": "chair@example.com", "X-Actor-Role": "chair"}
    decision = client.post(
        f"/api/v1/research-runs/{run_id}/decisions",
        json={
            "actor": "chair@example.com",
            "action": "APPROVE_THESIS",
            "target_id": thesis_id,
            "rationale": "Approved after the memo, counter-evidence, valuation, and IC reviews were checked.",
        },
        headers=chair_headers,
    )
    assert decision.status_code == 200, decision.text
    final_run = decision.json()
    assert final_run["decisions"][-1]["actor"] == "chair@example.com"
    assert len(final_run["ic_reviews"]) == 5

    memo = client.get(f"/api/v1/research-runs/{run_id}/memo")
    assert memo.status_code == 200, memo.text
    memo_payload = memo.json()
    assert memo_payload["thesis_id"] == thesis_id
    assert memo_payload["red_team_review_ids"]
    assert memo_payload["ic_review_ids"]
    assert memo_payload["financial_analysis_input_hash"] == financial.json()["input_hash"]
    assert memo_payload["valuation_scenarios_id"] == valuation.json()["id"]

    memory = client.get(f"/api/v1/research-runs/{run_id}/memory")
    assert memory.status_code == 200, memory.text
    assert final_run["decisions"][-1]["id"] in memory.json()["decision_ids"]
