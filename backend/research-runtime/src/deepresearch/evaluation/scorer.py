"""Evidence-based golden-case scorer."""

from typing import Any

from deepresearch.domain.models import EvaluationCheck, EvaluationResult, ResearchRun


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
