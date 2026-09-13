import json
from urllib.error import HTTPError
from urllib.parse import urlparse

import pytest

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
from deepresearch.runtime.evidence import (
    DeterministicEvidenceProvider,
    EvidenceProviderError,
    FinEvidenceClient,
    HttpEvidenceProvider,
)


def make_inputs() -> tuple[ResearchTask, ResearchCase]:
    return (
        ResearchTask(
            id="market",
            title="Market",
            purpose="Assess market structure",
            tool_name="external-evidence",
            evidence_requirements=[EvidenceRequirement(id="market-signal", description="market evidence")],
        ),
        ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME"),
    )


def evidence_object(*, status: str = "RETRIEVED", evidence_id: str = "ev-1", text: str = "ACME reported revenue of 100 in FY2025.") -> dict:
    return {
        "api_version": "v1",
        "evidence_id": evidence_id,
        "document_id": "doc-1",
        "source_type": "text",
        "score": 0.9,
        "content": {"text": text, "table": None, "visual_reference": None},
        "provenance": {"document_name": "ACME FY2025 filing", "page_number": 12, "source_url": "https://example.test/filing", "document_hash": "a" * 64},
        "financial": {"entity": "ACME", "metric": "revenue", "period": "FY2025", "unit": "USD", "category": None},
        "structure": {"table_id": None, "row_id": None, "column_id": None, "bbox": None},
        "verification": {"evidence_type": "TEXT", "confidence": 0.95, "coverage_status": status},
    }


def citation(*, evidence_id: str = "ev-1") -> dict:
    return {
        "api_version": "v1",
        "evidence_id": evidence_id,
        "document_id": "doc-1",
        "document_name": "ACME FY2025 filing",
        "page_number": 12,
        "source_url": "https://example.test/filing",
        "document_hash": "a" * 64,
        "table_id": None,
        "row_id": None,
        "column_id": None,
        "bbox": None,
    }


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = json.dumps(payload).encode()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class Router:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.paths: list[str] = []
        self.payloads: list[dict] = []

    def __call__(self, request, **kwargs):
        path = urlparse(request.full_url).path
        self.paths.append(path)
        if request.data:
            self.payloads.append(json.loads(request.data.decode()))
        response = self.responses[path]
        if isinstance(response, Exception):
            raise response
        return FakeResponse(response)


def test_deterministic_provider_marks_fixture_provenance() -> None:
    task, case = make_inputs()
    record = DeterministicEvidenceProvider().collect(task, case)[0]
    assert record.provenance_complete is True
    assert record.provenance["fixture"] is True


def test_http_provider_uses_search_coverage_and_citation_and_preserves_qualification(monkeypatch: pytest.MonkeyPatch) -> None:
    router = Router(
        {
            "/api/v1/evidence/search": {"api_version": "v1", "evidence": [evidence_object()], "catalog_size": 1},
            "/api/v1/evidence/coverage": {"api_version": "v1", "coverage_score": 1.0, "independent_coverage": 1.0, "critical_coverage": 1.0, "missing_requirements": [], "status": "ELIGIBLE", "evidence": [evidence_object(status="SUPPORTED")]},
            "/api/v1/evidence/ev-1/citation": citation(),
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)
    task, case = make_inputs()

    records = HttpEvidenceProvider("https://evidence.example").collect(task, case)

    assert [path for path in router.paths] == ["/api/v1/evidence/search", "/api/v1/evidence/coverage", "/api/v1/evidence/ev-1/citation"]
    assert "/v1/evidence/collect" not in router.paths
    assert router.payloads[0]["filters"] == {}
    assert router.payloads[1]["required_claims"][0]["requirement_id"] == "market-signal"
    assert records[0].id == "ev-1"
    assert records[0].qualification == "QUALIFIED"
    assert records[0].source_url == "https://example.test/filing"
    assert records[0].locator == "page:12"
    assert records[0].provenance["finevidence"]["evidence_id"] == "ev-1"


def test_http_provider_does_not_promote_partial_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    router = Router(
        {
            "/api/v1/evidence/search": {"api_version": "v1", "evidence": [evidence_object()], "catalog_size": 1},
            "/api/v1/evidence/coverage": {"api_version": "v1", "coverage_score": 0.5, "independent_coverage": 0.5, "critical_coverage": 0.0, "missing_requirements": ["market-signal"], "status": "PARTIAL", "evidence": [evidence_object(status="PARTIAL")]},
            "/api/v1/evidence/ev-1/citation": citation(),
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)
    task, case = make_inputs()

    assert HttpEvidenceProvider("https://evidence.example").collect(task, case)[0].qualification == "NEEDS_REVIEW"


def test_http_provider_bounds_long_page_excerpt(monkeypatch: pytest.MonkeyPatch) -> None:
    long_text = "source text " * 600
    router = Router(
        {
            "/api/v1/evidence/search": {"api_version": "v1", "evidence": [evidence_object(text=long_text)], "catalog_size": 1},
            "/api/v1/evidence/coverage": {"api_version": "v1", "coverage_score": 1.0, "independent_coverage": 1.0, "critical_coverage": 1.0, "missing_requirements": [], "status": "ELIGIBLE", "evidence": [evidence_object(status="SUPPORTED", text=long_text)]},
            "/api/v1/evidence/ev-1/citation": citation(),
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)
    task, case = make_inputs()

    record = HttpEvidenceProvider("https://evidence.example").collect(task, case)[0]

    assert len(record.excerpt) == 5000
    assert record.excerpt.endswith("complete source.]")


def test_http_provider_rejects_malformed_v1_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", lambda *args, **kwargs: FakeResponse({"api_version": "v2", "evidence": [], "catalog_size": 0}))
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="response contract invalid"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


@pytest.mark.parametrize("failure", [TimeoutError("timed out"), HTTPError("url", 503, "unavailable", {}, None)])
def test_http_provider_preserves_transport_failures(monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(failure))
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="provider"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


def test_http_provider_rejects_mismatched_citation(monkeypatch: pytest.MonkeyPatch) -> None:
    router = Router(
        {
            "/api/v1/evidence/search": {"api_version": "v1", "evidence": [evidence_object()], "catalog_size": 1},
            "/api/v1/evidence/coverage": {"api_version": "v1", "coverage_score": 1.0, "independent_coverage": 1.0, "critical_coverage": 1.0, "missing_requirements": [], "status": "ELIGIBLE", "evidence": [evidence_object(status="SUPPORTED")]},
            "/api/v1/evidence/ev-1/citation": citation(evidence_id="other"),
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="citation does not match"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


def test_client_exposes_frozen_auxiliary_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    router = Router(
        {
            "/health": {"status": "ok", "catalog_size": 1},
            "/api/v1/table/query": {"api_version": "v1", "evidence": []},
            "/api/v1/evidence/verify": {"api_version": "v1", "supported": True, "coverage_score": 1.0, "missing_requirements": [], "supporting_evidence": []},
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)
    client = FinEvidenceClient("https://evidence.example")

    assert client.health().status == "ok"
    assert client.table_query(entity="ACME").evidence == []
    assert client.verify("ACME revenue was 100", ["ev-1"]).supported is True
    assert router.paths == ["/health", "/api/v1/table/query", "/api/v1/evidence/verify"]


def test_http_provider_exposes_claim_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    router = Router(
        {
            "/api/v1/evidence/verify": {
                "api_version": "v1",
                "supported": True,
                "coverage_score": 1.0,
                "missing_requirements": [],
                "supporting_evidence": [],
            }
        }
    )
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", router)

    assert HttpEvidenceProvider("https://evidence.example").verify_claim("Observed claim", ["ev-1"]) is True
    assert router.payloads == [{"claim": "Observed claim", "evidence_ids": ["ev-1"]}]
