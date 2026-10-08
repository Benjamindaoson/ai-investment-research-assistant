"""Compare deterministic and LLM-generated plans on one live FinEvidence catalog."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from deepresearch.domain.models import ResearchCase, ResearchPlan, ResearchRun
from deepresearch.evaluation.llm_planner_regression import llm_golden_case
from deepresearch.evaluation.scorer import score_plan
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import HttpEvidenceProvider
from deepresearch.runtime.planner import DeterministicResearchPlanner, ResearchPlanner


class FixedPlanPlanner:
    supports_dynamic_tasks = True

    def __init__(self, plan: ResearchPlan) -> None:
        self.plan_value = plan
        self.name = plan.planner_name
        self.version = plan.planner_version

    def plan(self, case: ResearchCase) -> ResearchPlan:
        return self.plan_value.model_copy(deep=True)

    def replan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        del case, unresolved_requirement_ids
        return self.plan_value.model_copy(deep=True)


def _case() -> ResearchCase:
    return ResearchCase(
        id="LLM-PLANNER-REGRESSION-001",
        question="Assess ACME's revenue durability, margin resilience, competitive position, and downside risks.",
        target="ACME",
    )


def _metrics(run: ResearchRun) -> dict[str, Any]:
    requirements = [requirement for task in run.tasks for requirement in task.evidence_requirements]
    unresolved = [
        requirement
        for task in run.tasks
        for requirement in task.evidence_requirements
        if sum(
            record.qualification == "QUALIFIED"
            for record in run.evidence
            if record.task_id == task.id and record.requirement_id == requirement.id
        ) < requirement.minimum_records
    ]
    counter_requirements = [requirement for requirement in requirements if "COUNTER" in requirement.required_stances]
    counter_qualified = [
        requirement
        for task in run.tasks
        for requirement in task.evidence_requirements
        if "COUNTER" in requirement.required_stances
        and sum(
            record.qualification == "QUALIFIED" and record.stance == "COUNTER"
            for record in run.evidence
            if record.task_id == task.id and record.requirement_id == requirement.id
        ) >= requirement.minimum_records
    ]
    receipts = [item for item in run.tool_executions if item.operation == "CLAIM_VERIFICATION"]
    supported = [item for item in receipts if item.verification_supported is True]
    return {
        "state": run.state,
        "evidence_count": len(run.evidence),
        "qualified_evidence_rate": round(
            sum(item.qualification == "QUALIFIED" for item in run.evidence) / len(run.evidence), 4
        )
        if run.evidence
        else 0.0,
        "claim_count": len(run.claims),
        "claim_verification_receipt_count": len(receipts),
        "claim_verification_support_rate": round(len(supported) / len(receipts), 4) if receipts else None,
        "unresolved_requirement_rate": round(len(unresolved) / len(requirements), 4) if requirements else 0.0,
        "counter_evidence_coverage_rate": round(len(counter_qualified) / len(counter_requirements), 4)
        if counter_requirements
        else 0.0,
        "memo_status": run.memo.status if run.memo is not None else None,
        "memo_ready": bool(run.memo and run.memo.status == "READY_FOR_REVIEW" and run.state == "COMPLETED"),
        "memo_section_count": len(run.memo.sections) if run.memo else 0,
    }


def _execute(provider: HttpEvidenceProvider, planner: ResearchPlanner, directory: str) -> dict[str, Any]:
    engine = ResearchEngine(SQLiteStore(Path(directory) / f"{planner.name.replace(':', '-')}.sqlite3"), provider, planner=planner)
    run = engine.create_run(_case())
    completed = engine.execute(run.id)
    evaluation = engine.evaluate_run(
        completed.id,
        {
            "case_id": completed.case_id,
            "expected_state": "COMPLETED",
            "minimum_qualified_evidence": 1,
            "requires_claim": True,
        },
    )
    return {
        "planner": completed.plan.planner_name if completed.plan else planner.name,
        "plan_score": score_plan(completed.plan, llm_golden_case()).model_dump(mode="json") if completed.plan else None,
        "run_id": completed.id,
        "metrics": _metrics(completed),
        "evaluation": evaluation.model_dump(mode="json"),
    }


def compare(output_path: Path, llm_report_path: Path) -> dict[str, Any]:
    base_url = os.environ.get("FIN_EVIDENCE_BASE_URL") or os.environ.get("FINEVIDENCE_BASE_URL")
    if not base_url:
        raise ValueError("FIN_EVIDENCE_BASE_URL is required")
    llm_report = cast(dict[str, Any], json.loads(llm_report_path.read_text(encoding="utf-8")))
    plan = ResearchPlan.model_validate(llm_report["llm_plan"]["plan"])
    provider = HttpEvidenceProvider(base_url, float(os.environ.get("FIN_EVIDENCE_TIMEOUT_SECONDS", "60")))
    health = provider.client.health().model_dump(mode="json")
    with TemporaryDirectory(prefix="deepresearch-catalog-comparison-") as directory:
        deterministic = _execute(provider, DeterministicResearchPlanner(), directory)
        llm_plan_replay = _execute(provider, FixedPlanPlanner(plan), directory)
    report = {
        "schema": "finevidence-planner-comparison-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "catalog_observation": {"endpoint": base_url, **health, "same_endpoint_for_both_runs": True},
        "comparison": {
            "deterministic_planner": deterministic,
            "llm_generated_plan_replay": llm_plan_replay,
        },
        "interpretation": {
            "llm_run_is_plan_replay": True,
            "claim_verification_is_external_gate": True,
            "memo_ready_requires_completed_run_and_ready_for_review": True,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.output, args.llm_report)
    print(json.dumps({"status": "PASS", "report": str(args.output), "catalog_size": report["catalog_observation"]["catalog_size"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
