import json
from hashlib import sha256

import pytest

from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchRun,
    ResearchTask,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.synthesis import (
    LLMResearchSynthesizer,
    SynthesisClaimDraft,
    SynthesisDraft,
    SynthesisProviderError,
    SynthesisThesisDraft,
    create_configured_research_synthesizer,
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


def make_run(qualification: str = "QUALIFIED") -> ResearchRun:
    task = ResearchTask(
        id="market",
        title="Market structure",
        purpose="Assess market structure",
        tool_name="research",
        evidence_requirements=[EvidenceRequirement(id="market-signal", description="market evidence")],
    )
    evidence = EvidenceRecord(
        id="evidence-1",
        task_id="market",
        requirement_id="market-signal",
        stance="SUPPORTING",
        qualification=qualification,
        source_id="source-1",
        source_title="ACME filing",
        excerpt="Observed market evidence.",
        provider="fixture",
        source_url="https://example.test/source-1",
        locator="page:1",
        content_hash=sha256(b"evidence").hexdigest(),
    )
    return ResearchRun(id="run-1", case_id="case-1", tasks=[task], evidence=[evidence])


def draft_for(evidence_ids: list[str]) -> SynthesisDraft:
    return SynthesisDraft(
        claims=[SynthesisClaimDraft(task_id="market", statement="Market claim.", evidence_ids=evidence_ids, confidence=0.8)],
        thesis=SynthesisThesisDraft(statement="Thesis.", bull="Bull.", base="Base.", bear="Bear."),
    )


def test_llm_synthesis_returns_structured_draft_with_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    run = make_run()
    case = ResearchCase(id="case-1", question="Assess ACME market durability", target="ACME")
    payload = {"claims": [{"task_id": "market", "statement": "Market claim.", "evidence_ids": ["evidence-1"], "confidence": 0.8}], "thesis": {"statement": "Thesis.", "bull": "Bull.", "base": "Base.", "bear": "Bear."}}
    monkeypatch.setattr(
        "deepresearch.runtime.synthesis.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": json.dumps(payload)}}]}),
    )

    draft = LLMResearchSynthesizer("secret-value", "https://llm.example", "model").synthesize(case, run)

    assert draft.claims[0].evidence_ids == ["evidence-1"]
    assert draft.provenance["provider"] == "https://llm.example"
    assert len(draft.provenance["request_hash"]) == 64
    assert len(draft.provenance["response_hash"]) == 64
    assert "secret-value" not in json.dumps(draft.model_dump(mode="json"))


def test_llm_synthesis_rejects_malformed_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "deepresearch.runtime.synthesis.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": "not json"}}]}),
    )

    with pytest.raises(SynthesisProviderError, match="response contract invalid"):
        LLMResearchSynthesizer("secret", "https://llm.example", "model").synthesize(
            ResearchCase(id="case-1", question="Assess ACME market durability", target="ACME"), make_run()
        )


def test_synthesis_configuration_is_deterministic_by_default_and_explicit_for_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPRESEARCH_SYNTHESIZER", raising=False)
    assert create_configured_research_synthesizer().name == "deterministic-evidence-synthesis"
    monkeypatch.setenv("DEEPRESEARCH_SYNTHESIZER", "llm")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://llm.example")
    monkeypatch.setenv("DEEPSEEK_MODEL", "model")

    configured = create_configured_research_synthesizer()

    assert isinstance(configured, LLMResearchSynthesizer)


def test_engine_applies_valid_llm_synthesis_and_keeps_provenance(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    def respond(request, **kwargs):
        body = json.loads(request.data.decode())
        evidence = json.loads(body["messages"][1]["content"])["qualified_evidence"]
        payload = {
            "claims": [{"task_id": "market", "statement": "Market claim.", "evidence_ids": [evidence[0]["id"]], "confidence": 0.8}],
            "thesis": {"statement": "LLM thesis.", "bull": "LLM bull.", "base": "LLM base.", "bear": "LLM bear."},
        }
        return FakeResponse({"choices": [{"message": {"content": json.dumps(payload)}}]})

    monkeypatch.setattr("deepresearch.runtime.synthesis.urlopen", respond)
    synthesizer = LLMResearchSynthesizer("secret", "https://llm.example", "model")
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider(), synthesizer=synthesizer)
    case = ResearchCase(id="case-1", question="Assess ACME market durability", target="ACME")
    run = engine.create_run(case, [make_run().tasks[0]])

    result = engine.execute(run.id)

    assert result.state == "COMPLETED"
    assert result.claims[0].status == "QUALIFIED"
    assert result.thesis is not None
    assert result.thesis.statement == "LLM thesis."
    assert result.thesis.provenance["model"] == "model"


@pytest.mark.parametrize(
    ("qualification", "evidence_ids", "message"),
    [("QUALIFIED", ["missing"], "unknown evidence"), ("NEEDS_REVIEW", ["evidence-1"], "unqualified evidence")],
)
def test_engine_rejects_unsafe_synthesis_links(tmp_path, qualification, evidence_ids, message) -> None:
    class FixedProvider(DeterministicEvidenceProvider):
        qualification_authority = "external"

        def collect(self, task, case):
            return [make_run(qualification).evidence[0]]

    class ProposedSynthesizer:
        name = "test-synthesis"
        version = "v1"

        def synthesize(self, case, run):
            return draft_for(evidence_ids)

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), FixedProvider(), synthesizer=ProposedSynthesizer())
    run = engine.create_run(ResearchCase(id="case-1", question="Assess ACME market durability", target="ACME"), [make_run().tasks[0]])

    result = engine.execute(run.id)

    assert result.state == "FAILED"
    assert result.thesis is None
    assert message in engine.store.events(run.id)[-2]["payload"]["reason"]
