from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.persistence.store import SQLiteStore


def _request(client: TestClient, run_id: str, *, evidence: list[dict]) -> dict:
    supporting = next(item["id"] for item in evidence if item["stance"] == "SUPPORTING")
    counter = next(
        item["id"]
        for item in evidence
        if item["stance"] == "COUNTER" and item["qualification"] == "QUALIFIED"
    )
    links = {
        "revenue_growth_pct": [supporting],
        "operating_margin_pct": [supporting],
        "fcf_margin_pct": [supporting],
        "discount_rate_pct": [supporting],
        "terminal_growth_pct": [supporting],
        "net_cash": [supporting],
        "shares_outstanding": [supporting],
    }
    scenarios = [
        {
            "name": "BULL",
            "revenue_growth_pct": "15",
            "operating_margin_pct": "25",
            "fcf_margin_pct": "20",
            "discount_rate_pct": "10",
            "terminal_growth_pct": "3",
            "net_cash": "10",
            "shares_outstanding": "100",
            "evidence_ids": links,
        },
        {
            "name": "BASE",
            "revenue_growth_pct": "8",
            "operating_margin_pct": "20",
            "fcf_margin_pct": "15",
            "discount_rate_pct": "10",
            "terminal_growth_pct": "3",
            "net_cash": "10",
            "shares_outstanding": "100",
            "evidence_ids": links,
        },
        {
            "name": "BEAR",
            "revenue_growth_pct": "0",
            "operating_margin_pct": "12",
            "fcf_margin_pct": "8",
            "discount_rate_pct": "11",
            "terminal_growth_pct": "2",
            "net_cash": "10",
            "shares_outstanding": "100",
            "evidence_ids": links,
        },
    ]
    return {
        "financial_facts": {
            "period": "FY2025",
            "facts": [
                {
                    "field": "revenue",
                    "value": "120",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "prior_revenue",
                    "value": "100",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "operating_income",
                    "value": "24",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "operating_cash_flow",
                    "value": "20",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "capex",
                    "value": "5",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "cash",
                    "value": "30",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
                {
                    "field": "debt",
                    "value": "20",
                    "period": "FY2025",
                    "unit": "USD mm",
                    "currency": "USD",
                    "basis": "REPORTED",
                    "evidence_ids": [supporting],
                },
            ],
        },
        "valuation": {
            "base_revenue": "120",
            "base_revenue_evidence_ids": [supporting],
            "scenarios": scenarios,
        },
        "red_team": {
            "reviewer": "Independent analyst",
            "challenge": "The growth signal may not persist through the next cycle.",
            "evidence_ids": [counter],
            "outcome": "SUPPORTED",
            "rationale": "The counter-evidence is material to the downside case.",
        },
        "ic_reviews": [
            {
                "role": role,
                "reviewer": role.title(),
                "position": "MIXED" if role != "BULL" else "SUPPORTIVE",
                "recommendation": "HOLD" if role != "BULL" else "APPROVE",
                "rationale": f"The {role.lower()} review considered the linked evidence before sizing.",
                "evidence_ids": [supporting],
            }
            for role in ("BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER")
        ],
        "decision": {
            "actor": "IC chair",
            "action": "APPROVE_THESIS",
            "target_id": "placeholder",
            "rationale": "Approve after reviewing the evidence, counter-evidence, and scenario range.",
        },
    }


def test_complete_mvp_workflow_persists_the_full_artifact_chain(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME's margin durability", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    evidence = client.post(f"/api/v1/research-runs/{run_id}/execute").json()["evidence"]
    request = _request(client, run_id, evidence=evidence)
    thesis_id = client.get(f"/api/v1/research-runs/{run_id}").json()["thesis"]["id"]
    request["decision"]["target_id"] = thesis_id

    result = client.post(f"/api/v1/research-runs/{run_id}/mvp-complete", json=request)

    assert result.status_code == 200, result.text
    receipt = result.json()
    assert receipt["state"] == "COMPLETED"
    assert receipt["evaluation"]["passed"] is True
    assert len(receipt["ic_review_ids"]) == 5
    assert client.get(f"/api/v1/research-runs/{run_id}/financial-analysis").status_code == 200
    assert client.get(f"/api/v1/research-runs/{run_id}/valuation-scenarios").status_code == 200
    assert len(client.get(f"/api/v1/research-runs/{run_id}/red-team-reviews").json()) == 1
    assert len(client.get(f"/api/v1/research-runs/{run_id}/ic-reviews").json()) == 5
    assert client.get(f"/api/v1/research-runs/{run_id}/evaluation").status_code == 200
    assert client.get(f"/api/v1/research-runs/{run_id}/trace").json()["state"] == "COMPLETED"

    retry = client.post(f"/api/v1/research-runs/{run_id}/mvp-complete", json=request)
    assert retry.status_code == 200
    assert retry.json()["decision_id"] == receipt["decision_id"]


def test_mvp_workflow_rejects_missing_financial_evidence(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME downside", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    evidence = client.post(f"/api/v1/research-runs/{run_id}/execute").json()["evidence"]
    request = _request(client, run_id, evidence=evidence)
    request["financial_facts"]["facts"][0]["evidence_ids"] = ["missing-evidence"]
    request["decision"]["target_id"] = client.get(f"/api/v1/research-runs/{run_id}").json()["thesis"]["id"]

    result = client.post(f"/api/v1/research-runs/{run_id}/mvp-complete", json=request)

    assert result.status_code == 422
    assert "financial evidence not found" in result.json()["detail"]
    assert client.get(f"/api/v1/research-runs/{run_id}/financial-analysis").status_code == 404


def test_mvp_workflow_requires_all_ic_roles(tmp_path) -> None:
    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    created = client.post(
        "/api/v1/research-cases",
        json={"question": "Assess ACME risk", "target": "ACME"},
    )
    run_id = created.json()["run_id"]
    evidence = client.post(f"/api/v1/research-runs/{run_id}/execute").json()["evidence"]
    request = _request(client, run_id, evidence=evidence)
    request["ic_reviews"][-1]["role"] = "BULL"

    result = client.post(f"/api/v1/research-runs/{run_id}/mvp-complete", json=request)

    assert result.status_code == 422
