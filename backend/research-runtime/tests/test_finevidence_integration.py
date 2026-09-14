import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deepresearch.api import create_app
from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.evidence import (
    FinEvidenceClient,
    HttpEvidenceProvider,
    HttpTableEvidenceProvider,
)


@pytest.mark.integration
def test_real_finevidence_v1_chain_preserves_identity_and_provenance() -> None:
    if os.environ.get("FIN_EVIDENCE_INTEGRATION") != "1":
        pytest.skip("set FIN_EVIDENCE_INTEGRATION=1 to run the real service smoke")
    base_url = os.environ.get("FIN_EVIDENCE_BASE_URL")
    if not base_url:
        pytest.skip("FIN_EVIDENCE_BASE_URL is required for the real service smoke")
    timeout = float(os.environ.get("FIN_EVIDENCE_TIMEOUT_SECONDS", "60"))

    client = FinEvidenceClient(base_url, timeout)
    assert client.health().status == "ok"
    task = ResearchTask(
        id="finevidence-integration",
        title="HSBC evidence",
        purpose="Read back real provenance-bearing evidence from FinEvidence",
        tool_name="external-evidence",
        evidence_requirements=[
            EvidenceRequirement(
                id="hsbc-context",
                description="HSBC annual report context",
                fact_type="CONTEXT_FACT",
                role="context",
                entity="HSBC",
                criticality="OPTIONAL",
                evidence_role="CONTEXT_SUPPORT",
            )
        ],
    )
    case = ResearchCase(
        id="case-finevidence-integration",
        question="HSBC annual report context",
        target="HSBC",
    )

    records = HttpEvidenceProvider(base_url, timeout).collect(task, case)
    table_records = HttpTableEvidenceProvider(base_url, timeout).collect(task, case)
    assert records
    assert any(record.qualification == "QUALIFIED" for record in records)

    for expected_provider, provider_records in (
        ("finevidence-http", records),
        ("finevidence-table-http", table_records),
    ):
        for record in provider_records:
            assert record.provider == expected_provider
            assert record.provenance_complete
            finevidence = record.provenance["finevidence"]
            assert finevidence["api_version"] == "v1"
            assert finevidence["evidence_id"]
            assert finevidence["document_id"] == record.source_id
            assert finevidence["coverage_status"] in {"ELIGIBLE", "PARTIAL", "INSUFFICIENT"}
            assert finevidence["citation"]["evidence_id"] == finevidence["evidence_id"]
            assert finevidence["citation"]["document_id"] == finevidence["document_id"]
            assert finevidence["citation"]["source_url"] == record.source_url
            assert finevidence["citation"]["page_number"] >= 1
            assert len(record.content_hash or "") == 64
            if finevidence["coverage_status"] != "ELIGIBLE":
                assert record.qualification != "QUALIFIED"


@pytest.mark.integration
def test_real_finevidence_v1_api_run_chain(tmp_path: Path) -> None:
    if os.environ.get("FIN_EVIDENCE_INTEGRATION") != "1":
        pytest.skip("set FIN_EVIDENCE_INTEGRATION=1 to run the real service smoke")
    base_url = os.environ.get("FIN_EVIDENCE_BASE_URL")
    if not base_url:
        pytest.skip("FIN_EVIDENCE_BASE_URL is required for the real service smoke")

    client = TestClient(create_app(SQLiteStore(tmp_path / "runtime.sqlite3")))
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["evidence_mode"] == "LIVE_EXTERNAL"
    assert health.json()["evidence_provider"] == "finevidence-http"
    assert "financial-table" in health.json()["tools"]

    created = client.post(
        "/api/v1/research-cases",
        json={"question": "HSBC annual report context", "target": "HSBC"},
    )
    assert created.status_code == 201
    run_id = created.json()["run_id"]

    plan = client.get(f"/api/v1/research-runs/{run_id}/plan")
    assert plan.status_code == 200
    assert plan.json()["status"] == "VALIDATED"

    executed = client.post(f"/api/v1/research-runs/{run_id}/execute")
    assert executed.status_code == 200
    payload = executed.json()
    assert payload["state"] == "COMPLETED"
    assert payload["evidence"]
    assert any(item["qualification"] == "QUALIFIED" for item in payload["evidence"])
    for item in payload["evidence"]:
        assert item["provider"] == "finevidence-http"
        assert item["source_url"]
        assert item["locator"]
        assert len(item["content_hash"]) == 64
        finevidence = item["provenance"]["finevidence"]
        assert finevidence["api_version"] == "v1"
        assert finevidence["evidence_id"]
        assert finevidence["document_id"] == item["source_id"]
        assert finevidence["citation"]["evidence_id"] == finevidence["evidence_id"]
        assert finevidence["citation"]["document_id"] == finevidence["document_id"]

    memo = client.get(f"/api/v1/research-runs/{run_id}/memo")
    assert memo.status_code == 200
    assert memo.json()["status"] == "READY_FOR_REVIEW"

    events = client.get(f"/api/v1/research-runs/{run_id}/events")
    assert events.status_code == 200
    assert any(item["event_type"] == "RUN_COMPLETED" for item in events.json())
