import pytest

from deepresearch.domain.models import ResearchCase, ResearchPlan, ResearchTask
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.planner import DeterministicResearchPlanner


def test_deterministic_planner_returns_a_validated_financial_plan() -> None:
    case = ResearchCase(id="case-1", question="Assess ACME margin durability", target="ACME")

    plan = DeterministicResearchPlanner().plan(case)

    assert plan.status == "PROPOSED"
    assert plan.planner_name == "deterministic-financial-planner"
    assert len(plan.tasks) == 3
    assert plan.tasks[-1].depends_on == ["market", "fundamentals"]
    assert len(plan.input_hash) == 64


def test_engine_rejects_invalid_planner_output_before_persistence(tmp_path) -> None:
    class CyclicPlanner:
        name = "invalid-test-planner"
        version = "test-v1"

        def plan(self, case: ResearchCase) -> ResearchPlan:
            task_a = ResearchTask.model_construct(id="a", title="A", purpose="cycle", depends_on=["b"], tool_name="test", evidence_requirements=[])
            task_b = ResearchTask.model_construct(id="b", title="B", purpose="cycle", depends_on=["a"], tool_name="test", evidence_requirements=[])
            return ResearchPlan(case_id=case.id, question=case.question, planner_name=self.name, planner_version=self.version, input_hash="0" * 64, tasks=[task_a, task_b])

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicResearchPlanner(), planner=CyclicPlanner())
    case = ResearchCase(id="case-invalid", question="Assess ACME margin durability", target="ACME")

    with pytest.raises(ValueError, match="cycle"):
        engine.create_run(case)

    assert store.get_case(case.id) is None
