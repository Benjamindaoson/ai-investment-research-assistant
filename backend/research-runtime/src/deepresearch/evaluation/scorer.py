"""Evidence-based golden-case scorer."""

import json
from hashlib import sha256
from typing import Any

from deepresearch.domain.models import EvaluationCheck, EvaluationResult, ResearchPlan, ResearchRun
from deepresearch.runtime.engine import validate_task_dag


def evaluation_case_hash(case: dict[str, Any]) -> str:
    return sha256(json.dumps(case, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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
    return EvaluationResult(
        case_id=str(case["case_id"]),
        evaluator="deterministic-plan-scorer-v1",
        case_hash=evaluation_case_hash(case),
        passed=all(check.status == "PASS" for check in checks),
        checks=checks,
    )


def score_run(run: ResearchRun, case: dict[str, Any]) -> EvaluationResult:
    if case.get("requires_external_provider"):
        return EvaluationResult(
            case_id=str(case["case_id"]),
            evaluator="deterministic-run-scorer-v1",
            case_hash=evaluation_case_hash(case),
            passed=None,
            checks=[EvaluationCheck(name="external_provider", status="N/A", detail="FinEvidence provider is not configured in this local run.")],
        )
    checks: list[EvaluationCheck] = []
    expected_state = case.get("expected_state", "COMPLETED")
    checks.append(EvaluationCheck(name="terminal_state", status="PASS" if run.state == expected_state else "FAIL", detail=f"observed={run.state}, expected={expected_state}"))
    qualified_count = sum(item.qualification == "QUALIFIED" for item in run.evidence)
    minimum = int(case.get("minimum_qualified_evidence", 0))
    checks.append(EvaluationCheck(name="qualified_evidence", status="PASS" if qualified_count >= minimum else "FAIL", detail=f"observed={qualified_count}, minimum={minimum}"))
    if case.get("requires_claim", False):
        checks.append(EvaluationCheck(name="evidence_linked_claim", status="PASS" if any(claim.evidence_ids for claim in run.claims) else "FAIL", detail="at least one claim must link to evidence"))
    if run.state in {"COMPLETED", "PARTIAL"}:
        required_sections = {"thesis", "evidence", "risks", "scenarios", "decision"}
        sections = run.memo.sections if run.memo is not None else []
        section_keys = [section.section_key for section in sections]
        missing_sections = sorted(required_sections - set(section_keys))
        duplicate_sections = sorted({key for key in section_keys if section_keys.count(key) > 1})
        empty_sections = sorted(section.section_key for section in sections if not section.body.strip())
        checks.append(
            EvaluationCheck(
                name="memo_sections",
                status="PASS" if not missing_sections and not duplicate_sections and not empty_sections else "FAIL",
                detail=f"missing={missing_sections}, duplicates={duplicate_sections}, empty={empty_sections}",
            )
        )
        claim_ids = {claim.id for claim in run.claims}
        evidence_ids = {record.id for record in run.evidence}
        requirement_ids = {
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
        }
        dangling_claims = sorted({item for section in sections for item in section.claim_ids if item not in claim_ids})
        dangling_evidence = sorted({item for section in sections for item in section.evidence_ids if item not in evidence_ids})
        dangling_requirements = sorted(
            {
                item
                for section in sections
                for item in section.unresolved_requirement_ids
                if item not in requirement_ids
            }
        )
        checks.append(
            EvaluationCheck(
                name="memo_artifact_links",
                status="PASS" if not dangling_claims and not dangling_evidence and not dangling_requirements else "FAIL",
                detail=f"dangling_claims={dangling_claims}, dangling_evidence={dangling_evidence}, dangling_requirements={dangling_requirements}",
            )
        )
        evidence_by_id = {record.id: record for record in run.evidence}
        invalid_red_team_reviews = sorted(
            review.id
            for review in run.red_team_reviews
            if review.run_id != run.id
            or (run.thesis is not None and review.thesis_id != run.thesis.id)
        )
        dangling_red_team_evidence = sorted(
            {
                evidence_id
                for review in run.red_team_reviews
                for evidence_id in review.evidence_ids
                if evidence_id not in evidence_by_id
            }
        )
        invalid_red_team_stance = sorted(
            {
                evidence_id
                for review in run.red_team_reviews
                for evidence_id in review.evidence_ids
                if evidence_id in evidence_by_id
                and evidence_by_id[evidence_id].stance not in {"COUNTER", "CONFLICTING"}
            }
        )
        checks.append(
            EvaluationCheck(
                name="red_team_links",
                status="PASS"
                if not invalid_red_team_reviews
                and not dangling_red_team_evidence
                and not invalid_red_team_stance
                else "FAIL",
                detail=(
                    f"invalid_reviews={invalid_red_team_reviews}, "
                    f"dangling_evidence={dangling_red_team_evidence}, "
                    f"invalid_stance={invalid_red_team_stance}"
                ),
            )
        )
        if "minimum_red_team_reviews" in case:
            minimum_red_team_reviews = int(case.get("minimum_red_team_reviews", 0))
            valid_red_team_reviews = [
                review
                for review in run.red_team_reviews
                if review.id not in invalid_red_team_reviews
                and not any(
                    evidence_id in dangling_red_team_evidence or evidence_id in invalid_red_team_stance
                    for evidence_id in review.evidence_ids
                )
            ]
            checks.append(
                EvaluationCheck(
                    name="red_team_coverage",
                    status="PASS" if len(valid_red_team_reviews) >= minimum_red_team_reviews else "FAIL",
                    detail=f"observed={len(valid_red_team_reviews)}, minimum={minimum_red_team_reviews}",
                )
            )
        review_by_id = {review.id: review for review in run.ic_reviews}
        referenced_review_ids = set(run.memo.ic_review_ids if run.memo is not None else [])
        referenced_review_ids.update(review_id for decision in run.decisions for review_id in decision.review_ids)
        dangling_memo_reviews = sorted(
            set(run.memo.ic_review_ids if run.memo is not None else []) - review_by_id.keys()
        )
        dangling_decision_reviews = sorted(
            {review_id for decision in run.decisions for review_id in decision.review_ids} - review_by_id.keys()
        )
        invalid_reviews = sorted(
            review_id
            for review_id in referenced_review_ids & review_by_id.keys()
            if review_by_id[review_id].run_id != run.id
            or (run.thesis is not None and review_by_id[review_id].thesis_id != run.thesis.id)
        )
        checks.append(
            EvaluationCheck(
                name="ic_review_links",
                status="PASS"
                if not dangling_memo_reviews and not dangling_decision_reviews and not invalid_reviews
                else "FAIL",
                detail=(
                    f"dangling_memo={dangling_memo_reviews}, "
                    f"dangling_decisions={dangling_decision_reviews}, invalid_reviews={invalid_reviews}"
                ),
            )
        )
        if "required_ic_review_roles" in case:
            required_roles = {str(role) for role in (case.get("required_ic_review_roles") or [])}
            valid_reviews = [
                review
                for review in run.ic_reviews
                if review.run_id == run.id
                and (run.thesis is None or review.thesis_id == run.thesis.id)
            ]
            observed_roles = {review.role for review in valid_reviews}
            missing_roles = sorted(required_roles - observed_roles)
            checks.append(
                EvaluationCheck(
                    name="ic_review_coverage",
                    status="PASS" if not missing_roles else "FAIL",
                    detail=f"missing_roles={missing_roles}, observed_roles={sorted(observed_roles)}",
                )
            )
    statuses = {check.status for check in checks}
    passed = "FAIL" not in statuses
    return EvaluationResult(
        case_id=str(case["case_id"]),
        evaluator="deterministic-run-scorer-v1",
        case_hash=evaluation_case_hash(case),
        passed=passed,
        checks=checks,
    )
