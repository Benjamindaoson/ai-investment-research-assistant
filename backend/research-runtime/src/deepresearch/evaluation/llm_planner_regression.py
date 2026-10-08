"""Explicit, secret-safe regression runner for the configured LLM planner."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from deepresearch.domain.models import ResearchCase
from deepresearch.evaluation.scorer import score_plan
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import HttpEvidenceProvider
from deepresearch.runtime.planner import (
    DeterministicResearchPlanner,
    ResearchPlanner,
    create_configured_research_planner,
)


def _load_case(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(
        (Path(__file__).parents[3] / "evaluation" / "cases" / name).read_text(encoding="utf-8")
    ))


def golden_case() -> dict[str, Any]:
    return _load_case("planner.json")


def llm_golden_case() -> dict[str, Any]:
    return _load_case("llm_planner.json")


def live_configuration() -> dict[str, str | bool]:
    return {
        "planner_mode": os.environ.get("DEEPRESEARCH_PLANNER", "deterministic").strip().lower(),
        "llm_base_url": os.environ.get("DEEPSEEK_BASE_URL") or os.environ.get("LLM_BASE_URL") or "",
        "llm_model": os.environ.get("DEEPSEEK_MODEL") or os.environ.get("LLM_MODEL") or "",
        "llm_api_key_present": bool(os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")),
        "finevidence_base_url": os.environ.get("FIN_EVIDENCE_BASE_URL") or os.environ.get("FINEVIDENCE_BASE_URL") or "",
    }


def missing_live_configuration(config: dict[str, str | bool]) -> list[str]:
    required = {
        "DEEPRESEARCH_PLANNER=llm": config["planner_mode"] == "llm",
        "LLM API key": bool(config["llm_api_key_present"]),
        "LLM base URL": bool(config["llm_base_url"]),
        "LLM model": bool(config["llm_model"]),
        "FIN_EVIDENCE_BASE_URL": bool(config["finevidence_base_url"]),
    }
    return [name for name, present in required.items() if not present]


def _checks(result: Any) -> list[dict[str, Any]]:
    return [check.model_dump(mode="json") for check in result.checks]


def _plan_metrics(plan: Any) -> dict[str, int]:
    return {
        "task_count": len(plan.tasks),
        "dependency_edge_count": sum(len(task.depends_on) for task in plan.tasks),
        "evidence_requirement_count": sum(len(task.evidence_requirements) for task in plan.tasks),
        "counter_requirement_count": sum(
            any("COUNTER" in requirement.required_stances for requirement in task.evidence_requirements)
            for task in plan.tasks
        ),
    }


def _run_metrics(run: Any) -> dict[str, Any]:
    qualified = sum(item.qualification == "QUALIFIED" for item in run.evidence)
    linked_claims = sum(bool(claim.evidence_ids) for claim in run.claims)
    sections = run.memo.sections if run.memo is not None else []
    return {
        "state": run.state,
        "evidence_count": len(run.evidence),
        "qualified_evidence_count": qualified,
        "needs_review_evidence_count": sum(item.qualification == "NEEDS_REVIEW" for item in run.evidence),
        "unqualified_evidence_count": sum(item.qualification == "UNQUALIFIED" for item in run.evidence),
        "claim_count": len(run.claims),
        "linked_claim_count": linked_claims,
        "thesis_present": run.thesis is not None,
        "memo_status": run.memo.status if run.memo is not None else None,
        "memo_section_keys": [section.section_key for section in sections],
        "non_empty_memo_section_count": sum(bool(section.body.strip()) for section in sections),
    }


def _write_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_regression(output_path: Path) -> dict[str, Any]:
    config = live_configuration()
    missing = missing_live_configuration(config)
    report: dict[str, Any] = {
        "schema": "llm-planner-regression-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "configuration": config,
        "status": "BLOCKED" if missing else "RUNNING",
        "gates": {"configuration": "BLOCKED" if missing else "PASS"},
    }
    if missing:
        report["blocked_reasons"] = missing
        _write_report(output_path, report)
        return report

    case = ResearchCase(
        id="LLM-PLANNER-REGRESSION-001",
        question="Assess ACME's revenue durability, margin resilience, competitive position, and downside risks.",
        target="ACME",
    )
    baseline = DeterministicResearchPlanner().plan(case)
    baseline_score = score_plan(baseline, golden_case())
    report["baseline"] = {
        "planner": baseline.planner_name,
        "version": baseline.planner_version,
        "metrics": _plan_metrics(baseline),
        "score": baseline_score.model_dump(mode="json"),
    }

    try:
        planner: ResearchPlanner = create_configured_research_planner()
        finevidence_url = str(config["finevidence_base_url"])
        provider = HttpEvidenceProvider(finevidence_url, float(os.environ.get("FIN_EVIDENCE_TIMEOUT_SECONDS", "60")))
        with TemporaryDirectory(prefix="deepresearch-llm-regression-") as directory:
            engine = ResearchEngine(SQLiteStore(Path(directory) / "runtime.sqlite3"), provider, planner=planner)
            run = engine.create_run(case)
            plan = run.plan
            if plan is None:
                raise RuntimeError("runtime created a run without a plan")
            llm_score = score_plan(plan, llm_golden_case())
            report["llm_plan"] = {
                "planner": plan.planner_name,
                "version": plan.planner_version,
                "input_hash": plan.input_hash,
                "provenance": plan.provenance,
                "metrics": _plan_metrics(plan),
                "plan": plan.model_dump(mode="json"),
                "score": llm_score.model_dump(mode="json"),
            }
            report["gates"]["llm_plan"] = "PASS" if llm_score.passed else "FAIL"
            completed = engine.execute(run.id)
            run_score = engine.evaluate_run(
                completed.id,
                {
                    "case_id": completed.case_id,
                    "expected_state": "COMPLETED",
                    "minimum_qualified_evidence": 1,
                    "requires_claim": True,
                },
            )
            report["run"] = {
                "run_id": completed.id,
                "metrics": _run_metrics(completed),
                "score": run_score.model_dump(mode="json"),
                "provider": getattr(provider, "name", provider.__class__.__name__),
            }
            report["gates"].update(
                {
                    "runtime": "PASS" if completed.state == "COMPLETED" else "FAIL",
                    "evidence_qualification": "PASS" if any(item.qualification == "QUALIFIED" for item in completed.evidence) else "FAIL",
                    "memo": "PASS"
                    if completed.memo is not None
                    and completed.memo.status == "READY_FOR_REVIEW"
                    and all(section.body.strip() for section in completed.memo.sections)
                    else "FAIL",
                    "run_evaluation": "PASS" if run_score.passed else "FAIL",
                }
            )
            report["status"] = "PASS" if all(value == "PASS" for value in report["gates"].values()) else "FAIL"
    except Exception as error:  # noqa: BLE001 - report the bounded regression failure, then exit non-zero in CLI
        report["status"] = "FAIL"
        report["failure"] = {"type": error.__class__.__name__, "message": str(error)}
        report["gates"]["runtime"] = "FAIL"

    _write_report(output_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="JSON report path")
    args = parser.parse_args()
    report = run_regression(args.output)
    print(json.dumps({"status": report["status"], "report": str(args.output)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
