import json
from urllib.error import HTTPError

import pytest

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
from deepresearch.runtime.evidence import (
    DeterministicEvidenceProvider,
    EvidenceProviderError,
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


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = json.dumps(payload).encode()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def test_deterministic_provider_marks_fixture_provenance() -> None:
    task, case = make_inputs()
    record = DeterministicEvidenceProvider().collect(task, case)[0]
    assert record.provenance_complete is True
    assert record.provenance["fixture"] is True


def test_http_provider_rejects_unsupported_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", lambda *args, **kwargs: FakeResponse({"schema_version": 2, "records": []}))
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="unsupported provider schema version"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


def test_http_provider_rejects_malformed_record(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", lambda *args, **kwargs: FakeResponse({"schema_version": 1, "records": [{"task_id": "market"}]}))
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="response contract invalid"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


@pytest.mark.parametrize("failure", [TimeoutError("timed out"), HTTPError("url", 503, "unavailable", {}, None)])
def test_http_provider_preserves_transport_failures(monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise failure

    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", fail)
    task, case = make_inputs()
    with pytest.raises(EvidenceProviderError, match="provider"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)


def test_http_provider_rejects_evidence_for_another_task(monkeypatch: pytest.MonkeyPatch) -> None:
    task, case = make_inputs()
    record = DeterministicEvidenceProvider().collect(task, case)[0].model_dump(mode="json")
    record["task_id"] = "other-task"
    monkeypatch.setattr("deepresearch.runtime.evidence.urlopen", lambda *args, **kwargs: FakeResponse({"schema_version": 1, "records": [record]}))
    with pytest.raises(EvidenceProviderError, match="outside the requested task"):
        HttpEvidenceProvider("https://evidence.example").collect(task, case)
