import pytest

from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchTask,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider, EvidenceProviderError
from deepresearch.runtime.tools import ResearchToolRegistry


def make_task(tool_name: str) -> ResearchTask:
    return ResearchTask(
        id="market",
        title="Market",
        purpose="Assess market structure",
        tool_name=tool_name,
        evidence_requirements=[EvidenceRequirement(id="market-signal", description="market evidence")],
    )


def test_registry_resolves_registered_provider_and_compatibility_aliases() -> None:
    provider = DeterministicEvidenceProvider()
    registry = ResearchToolRegistry({"special": provider})

    assert registry.names == ("special",)
    assert registry.resolve("special") is provider
    with pytest.raises(EvidenceProviderError, match="not registered"):
        registry.resolve("missing")

    compatibility = ResearchToolRegistry.from_provider(provider)
    assert "deterministic-research" in compatibility.names
    assert compatibility.resolve("evidence.search") is provider


def test_registry_rejects_invalid_tool_registration() -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        ResearchToolRegistry({"": DeterministicEvidenceProvider()})
    with pytest.raises(TypeError, match="must expose collect"):
        ResearchToolRegistry({"invalid": object()})  # type: ignore[arg-type]


def test_engine_dispatches_registered_tool_and_fails_unknown_tool(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    provider.name = "special-provider"
    registry = ResearchToolRegistry({"special": provider})
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider, tool_registry=registry)
    case = ResearchCase(id="case-tool-registry", question="Assess ACME market", target="ACME")

    selected = engine.create_run(case, [make_task("special")])
    selected_result = engine.execute(selected.id)
    assert selected_result.state == "COMPLETED"
    assert provider.calls == ["market"]
    assert selected_result.tool_executions[0].provider == "special-provider"

    unknown = engine.create_run(case, [make_task("missing")])
    unknown_result = engine.execute(unknown.id)
    assert unknown_result.state == "FAILED"
    assert unknown_result.tasks[0].state == "FAILED"
    assert unknown_result.tool_executions[0].provider == "unregistered"
    assert unknown_result.tool_executions[0].status == "FAILED"
    assert "not registered: missing" in (unknown_result.tool_executions[0].error_message or "")
    assert provider.calls == ["market"]


def test_engine_uses_selected_provider_for_qualification(tmp_path) -> None:
    class ExternalProvider:
        name = "external"
        qualification_authority = "external"

        def collect(self, task, case):
            return [
                EvidenceRecord(
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    qualification="QUALIFIED",
                    source_id="external-source",
                    source_title="External source",
                    excerpt="Provider-qualified evidence.",
                    provider=self.name,
                    source_url="https://example.test/source",
                    locator="page:1",
                    content_hash="a" * 64,
                    provenance={},
                )
            ]

    deterministic = DeterministicEvidenceProvider()
    engine = ResearchEngine(
        SQLiteStore(tmp_path / "runtime.sqlite3"),
        deterministic,
        tool_registry=ResearchToolRegistry({"external": ExternalProvider()}),
    )
    run = engine.create_run(
        ResearchCase(id="case-tool-qualification", question="Assess ACME evidence", target="ACME"),
        [make_task("external")],
    )

    result = engine.execute(run.id)

    assert result.state == "COMPLETED"
    assert result.evidence[0].qualification == "QUALIFIED"
    assert deterministic.calls == []
    assert result.tool_executions[0].provider == "external"
