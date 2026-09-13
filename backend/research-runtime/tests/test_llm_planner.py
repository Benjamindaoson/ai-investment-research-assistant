import json
from urllib.error import HTTPError

import pytest

from deepresearch.domain.models import ResearchCase
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.planner import (
    DeterministicResearchPlanner,
    LLMResearchPlanner,
    PlannerProviderError,
    create_configured_research_planner,
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


def test_llm_planner_returns_structured_plan_without_secret_in_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
    tasks = DeterministicResearchPlanner().plan(case).tasks
    monkeypatch.setattr(
        "deepresearch.runtime.planner.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": json.dumps({"tasks": [task.model_dump(mode="json") for task in tasks]})}}]}),
    )

    plan = LLMResearchPlanner("secret-value", "https://llm.example", "deepseek-test").plan(case)

    assert plan.planner_name == "llm:deepseek-test"
    assert plan.provenance["provider"] == "https://llm.example"
    assert len(plan.provenance["request_hash"]) == 64
    assert len(plan.provenance["response_hash"]) == 64
    assert "secret-value" not in json.dumps(plan.model_dump(mode="json"))


def test_llm_planner_rejects_malformed_model_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "deepresearch.runtime.planner.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": "not json"}}]}),
    )
    with pytest.raises(PlannerProviderError, match="response contract invalid"):
        LLMResearchPlanner("secret", "https://llm.example", "model").plan(
            ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
        )


def test_llm_planner_accepts_json_markdown_fence(monkeypatch: pytest.MonkeyPatch) -> None:
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
    tasks = DeterministicResearchPlanner().plan(case).tasks
    content = "```json\n" + json.dumps({"tasks": [task.model_dump(mode="json") for task in tasks]}) + "\n```"
    monkeypatch.setattr(
        "deepresearch.runtime.planner.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": content}}]}),
    )

    plan = LLMResearchPlanner("secret", "https://llm.example", "model").plan(case)

    assert len(plan.tasks) == 3


def test_llm_planner_prompt_requires_evidence_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
    tasks = DeterministicResearchPlanner().plan(case).tasks
    requests: list[object] = []

    def respond(request: object, **kwargs: object) -> FakeResponse:
        requests.append(request)
        return FakeResponse({"choices": [{"message": {"content": json.dumps({"tasks": [task.model_dump(mode="json") for task in tasks]})}}]})

    monkeypatch.setattr("deepresearch.runtime.planner.urlopen", respond)
    LLMResearchPlanner("secret", "https://llm.example", "model").plan(case)

    body = json.loads(requests[0].data.decode())  # type: ignore[attr-defined]
    system_prompt = body["messages"][0]["content"]
    assert '"evidence_requirements"' in system_prompt
    assert "Do not include rationale" in system_prompt
    assert "3 to 5 tasks" in system_prompt


def test_llm_planner_rejects_overlarge_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
    tasks = DeterministicResearchPlanner().plan(case).tasks
    for index in range(3):
        tasks.append(tasks[-1].model_copy(update={"id": f"extra-{index}", "title": f"Extra task {index}"}))
    monkeypatch.setattr(
        "deepresearch.runtime.planner.urlopen",
        lambda *args, **kwargs: FakeResponse({"choices": [{"message": {"content": json.dumps({"tasks": [task.model_dump(mode="json") for task in tasks]})}}]}),
    )

    with pytest.raises(PlannerProviderError, match="response contract invalid"):
        LLMResearchPlanner("secret", "https://llm.example", "model").plan(case)


def test_llm_planner_preserves_http_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise HTTPError("url", 429, "rate limited", {}, None)

    monkeypatch.setattr("deepresearch.runtime.planner.urlopen", fail)
    with pytest.raises(PlannerProviderError, match="HTTP 429"):
        LLMResearchPlanner("secret", "https://llm.example", "model").plan(
            ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")
        )


def test_planner_configuration_is_deterministic_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPRESEARCH_PLANNER", raising=False)
    assert isinstance(create_configured_research_planner(), DeterministicResearchPlanner)


def test_llm_configuration_fails_fast_without_required_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPRESEARCH_PLANNER", "llm")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        create_configured_research_planner()


def test_selected_planner_failure_does_not_persist_a_partial_run(tmp_path) -> None:
    class FailingPlanner:
        name = "llm:failing"
        version = "v1"

        def plan(self, case: ResearchCase):
            raise PlannerProviderError("provider timed out")

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider(), planner=FailingPlanner())
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")

    with pytest.raises(PlannerProviderError, match="timed out"):
        engine.create_run(case)

    assert store.get_case(case.id) is None
