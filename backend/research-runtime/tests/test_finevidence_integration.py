import os

import pytest

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
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
