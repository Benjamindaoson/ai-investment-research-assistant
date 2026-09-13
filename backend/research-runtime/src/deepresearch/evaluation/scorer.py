"""Evidence-based golden-case scorer."""

from typing import Any

from deepresearch.domain.models import EvaluationCheck, EvaluationResult, ResearchPlan, ResearchRun
from deepresearch.runtime.engine import validate_task_dag


def score_plan(plan: ResearchPlan, case: dict[str, Any]) -> EvaluationResult:
    """Evaluate plan structure only; this never executes tools or touches storage."""
    checks: list[EvaluationCheck] = []
    actual_ids = {task.id for task in plan.tasks}
    required_ids = {str(task_id) for task_id in case.get("required_task_ids", [])}
    missing_ids = sorted(required_ids - actual_ids)
    minimum = int(case.get("minimum_task_count", 0))
    checks.append(
        EvaluationCheck(
            name="task_coverage",
            status="PASS" if not missing_ids and len(actual_ids) >= minimum else "FAIL",
            detail=f"missing={missing_ids}, observed={len(actual_ids)}, minimum={minimum}",
        )
    )

    try:
        validate_task_dag(plan.tasks)
        actual_dependencies = {task.id: sorted(task.depends_on) for task in plan.tasks}
        expected_dependencies = {
            str(task_id): sorted(str(item) for item in dependencies)
            for task_id, dependencies in dict(case.get("expected_dependencies", {})).items()
        }
        checks.append(
            EvaluationCheck(
                name="dependency_edges",
                status="PASS" if all(actual_dependencies.get(task_id) == dependencies for task_id, dependencies in expected_dependencies.items()) else "FAIL",
                detail=f"observed={actual_dependencies}, expected={expected_dependencies}",
            )
        )
    except ValueError as error:
        checks.append(EvaluationCheck(name="dependency_edges", status="FAIL", detail=f"invalid DAG: {error}"))

    required_evidence_tasks = {str(task_id) for task_id in case.get("required_evidence_task_ids", [])}
    missing_evidence_tasks = sorted(
        task_id
        for task_id in required_evidence_tasks
        if not any(task.id == task_id and task.evidence_requirements for task in plan.tasks)
    )
    checks.append(
        EvaluationCheck(
            name="evidence_requirements",
            status="PASS" if not missing_evidence_tasks else "FAIL",
            detail=f"missing_task_ids={missing_evidence_tasks}",
        )
    )

    counter_tasks = {str(task_id) for task_id in case.get("required_counter_evidence_task_ids", [])}
    missing_counter_tasks = sorted(
        task_id
        for task_id in counter_tasks
        if not any(
            task.id == task_id and any("COUNTER" in requirement.required_stances for requirement in task.evidence_requirements)
            for task in plan.tasks
        )
    )
    checks.append(
        EvaluationCheck(
            name="counter_evidence",
            status="PASS" if not missing_counter_tasks else "FAIL",
            detail=f"missing_task_ids={missing_counter_tasks}",
        )
    )

    maximum = int(case.get("maximum_task_count", len(plan.tasks)))
    checks.append(
        EvaluationCheck(
            name="task_ceiling",
            status="PASS" if len(plan.tasks) <= maximum else "FAIL",
            detail=f"observed={len(plan.tasks)}, maximum={maximum}",
        )
    )
    titles = [task.title.strip().casefold() for task in plan.tasks]
    duplicate_titles = sorted({title for title in titles if titles.count(title) > 1})
    checks.append(
        EvaluationCheck(
            name="duplicate_tasks",
            status="PASS" if len(actual_ids) == len(plan.tasks) and not duplicate_titles else "FAIL",
            detail=f"duplicate_titles={duplicate_titles}",
        )
    )
    return EvaluationResult(case_id=str(case["case_id"]), passed=all(check.status == "PASS" for check in checks), checks=checks)


def score_run(run: ResearchRun, case: dict[str, Any]) -> EvaluationResult:
    if case.get("requires_external_provider"):
        return EvaluationResult(case_id=str(case["case_id"]), passed=None, checks=[EvaluationCheck(name="external_provider", status="N/A", detail="FinEvidence provider is not configured in this local run.")])
    checks: list[EvaluationCheck] = []
    expected_state = case.get("expected_state", "COMPLETED")
    checks.append(EvaluationCheck(name="terminal_state", status="PASS" if run.state == expected_state else "FAIL", detail=f"observed={run.state}, expected={expected_state}"))
    qualified_count = sum(item.qualification == "QUALIFIED" for item in run.evidence)
    minimum = int(case.get("minimum_qualified_evidence", 0))
    checks.append(EvaluationCheck(name="qualified_evidence", status="PASS" if qualified_count >= minimum else "FAIL", detail=f"observed={qualified_count}, minimum={minimum}"))
    if case.get("requires_claim", False):
        checks.append(EvaluationCheck(name="evidence_linked_claim", status="PASS" if any(claim.evidence_ids for claim in run.claims) else "FAIL", detail="at least one claim must link to evidence"))
    statuses = {check.status for check in checks}
    passed = "FAIL" not in statuses
    return EvaluationResult(case_id=str(case["case_id"]), passed=passed, checks=checks)
