import json
from pathlib import Path

from deepresearch.domain.models import ResearchCase
from deepresearch.evaluation.scorer import score_plan
from deepresearch.runtime.planner import DeterministicResearchPlanner


def golden_case() -> dict[str, object]:
    return json.loads((Path(__file__).parents[1] / "evaluation" / "cases" / "planner.json").read_text(encoding="utf-8"))


def test_deterministic_plan_passes_independent_golden_case() -> None:
    case = ResearchCase(id="PL-001", question="Assess AI infrastructure margin durability", target="ACME")
    result = score_plan(DeterministicResearchPlanner().plan(case), golden_case())

    assert result.passed is True
    assert {check.name for check in result.checks} == {
        "task_coverage",
        "dependency_edges",
        "evidence_requirements",
        "counter_evidence",
        "task_ceiling",
        "duplicate_tasks",
    }
    assert all(check.status == "PASS" for check in result.checks)


def test_plan_evaluation_names_missing_coverage_and_counter_evidence() -> None:
    case = ResearchCase(id="PL-001", question="Assess AI infrastructure margin durability", target="ACME")
    plan = DeterministicResearchPlanner().plan(case)
    plan.tasks = plan.tasks[:2]
    result = score_plan(plan, golden_case())

    assert result.passed is False
    checks = {check.name: check for check in result.checks}
    assert checks["task_coverage"].status == "FAIL"
    assert "risk" in checks["task_coverage"].detail
    assert checks["counter_evidence"].status == "FAIL"


def test_model_agnostic_plan_contract_checks_evidence_counter_and_tools() -> None:
    case = ResearchCase(id="LLM-PLANNER-REGRESSION-001", question="Assess ACME durability", target="ACME")
    evaluation_case = json.loads(
        (Path(__file__).parents[1] / "evaluation" / "cases" / "llm_planner.json").read_text(encoding="utf-8")
    )

    result = score_plan(DeterministicResearchPlanner().plan(case), evaluation_case)

    assert result.passed is True
    assert {check.name for check in result.checks} >= {
        "all_tasks_have_evidence_requirements",
        "counter_evidence_anywhere",
        "tool_contract",
    }
