"""Deterministic, dependency-aware research execution."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from hashlib import sha256

from deepresearch.domain.models import (
    Checkpoint,
    Claim,
    DecisionRecord,
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchRun,
    ResearchTask,
    Thesis,
    ToolExecution,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.evidence import EvidenceProvider, evidence_hash


def validate_task_dag(tasks: Iterable[ResearchTask]) -> list[str]:
    task_list = list(tasks)
    ids = {task.id for task in task_list}
    if len(ids) != len(task_list):
        raise ValueError("task ids must be unique")
    for task in task_list:
        unknown = set(task.depends_on) - ids
        if unknown:
            raise ValueError(f"task {task.id} depends on unknown tasks: {sorted(unknown)}")
    incoming = {task.id: set(task.depends_on) for task in task_list}
    ordered: list[str] = []
    while incoming:
        ready = sorted(task_id for task_id, dependencies in incoming.items() if not dependencies)
        if not ready:
            raise ValueError("task dependency cycle detected")
        ordered.extend(ready)
        for task_id in ready:
            incoming.pop(task_id)
        for dependencies in incoming.values():
            dependencies.difference_update(ready)
    return ordered


class ResearchEngine:
    def __init__(self, store: SQLiteStore, provider: EvidenceProvider) -> None:
        self.store = store
        self.provider = provider

    def create_run(self, case: ResearchCase, tasks: list[ResearchTask] | None = None) -> ResearchRun:
        task_list = tasks or self._default_tasks()
        validate_task_dag(task_list)
        run = ResearchRun(id=f"run-{case.id}", case_id=case.id, tasks=task_list)
        self.store.save_case(case.model_dump(mode="json"))
        self.store.save_run(run.model_dump(mode="json"))
        self.store.append_event(run.id, "CASE_CREATED", {"case_id": case.id, "question": case.question})
        self.store.append_event(run.id, "RUN_CREATED", {"task_ids": [task.id for task in task_list]})
        return run

    def get_run(self, run_id: str) -> ResearchRun:
        payload = self.store.get_run(run_id)
        if payload is None:
            raise KeyError(run_id)
        return ResearchRun.model_validate(payload)

    def get_case(self, case_id: str) -> ResearchCase:
        payload = self.store.get_case(case_id)
        if payload is None:
            raise KeyError(case_id)
        return ResearchCase.model_validate(payload)

    def execute(self, run_id: str, stop_after_tasks: int | None = None) -> ResearchRun:
        run = self.get_run(run_id)
        if run.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"}:
            return run
        case = self.get_case(run.case_id)
        completed = {task.id for task in run.tasks if task.state == "COMPLETED"}
        if completed:
            self.store.append_event(run.id, "RUN_RESUMED", {"completed_task_ids": sorted(completed)})
        executed_this_call = 0
        while len(completed) < len(run.tasks):
            ready = [
                task for task in run.tasks if task.state == "PENDING" and set(task.depends_on) <= completed
            ]
            if not ready:
                return self._fail(run, "no ready task; DAG is inconsistent")
            for task in sorted(ready, key=lambda item: item.id):
                task.state = "RUNNING"
                run.state = "RUNNING"
                self._persist(run, "TASK_STARTED", {"task_id": task.id})
                records = self.provider.collect(task, case)
                qualified = [self._qualify(record, task) for record in records]
                run.evidence.extend(qualified)
                result_hash = evidence_hash(qualified) if qualified else sha256(b"empty").hexdigest()
                run.tool_executions.append(
                    ToolExecution(task_id=task.id, tool_name=task.tool_name, status="SUCCEEDED", result_hash=result_hash)
                )
                task.state = "COMPLETED"
                completed.add(task.id)
                executed_this_call += 1
                self._persist(run, "TASK_COMPLETED", {"task_id": task.id, "evidence_count": len(qualified)})
                self._checkpoint(run, completed)
                if stop_after_tasks is not None and executed_this_call >= stop_after_tasks:
                    return run
        run.state = "VERIFYING"
        self._persist(run, "RUN_VERIFYING", {})
        self._synthesize(run)
        run.completed_at = datetime.now(UTC)
        run.state = "COMPLETED" if all(self._task_is_qualified(run, task) for task in run.tasks) else "PARTIAL"
        self._persist(run, "RUN_COMPLETED" if run.state == "COMPLETED" else "RUN_PARTIAL", {"claim_count": len(run.claims)})
        return run

    def record_decision(self, run_id: str, decision: DecisionRecord) -> ResearchRun:
        run = self.get_run(run_id)
        if decision.target_id != (run.thesis.id if run.thesis else decision.target_id):
            raise ValueError("decision target does not belong to this run")
        if decision.action == "APPROVE_THESIS":
            if run.thesis is None or run.state != "COMPLETED":
                raise ValueError("only a completed run can approve a thesis")
            run.thesis.review_status = "APPROVED"
        elif decision.action == "REJECT_THESIS" and run.thesis is not None:
            run.thesis.review_status = "NEEDS_REVIEW"
        run.decisions.append(decision)
        self._persist(run, "HUMAN_DECISION", decision.model_dump(mode="json"))
        return run

    def _default_tasks(self) -> list[ResearchTask]:
        return [
            ResearchTask(id="market", title="Market structure", purpose="Assess market growth and competitive structure", tool_name="deterministic-research", evidence_requirements=[EvidenceRequirement(id="market-signal", description="market evidence")]),
            ResearchTask(id="fundamentals", title="Financial fundamentals", purpose="Assess revenue, margin, cash flow and balance-sheet durability", tool_name="deterministic-research", evidence_requirements=[EvidenceRequirement(id="fundamental-signal", description="financial evidence")]),
            ResearchTask(id="risk", title="Downside and disconfirming evidence", purpose="Test risks and conditions that would invalidate the thesis", depends_on=["market", "fundamentals"], tool_name="deterministic-research", evidence_requirements=[EvidenceRequirement(id="risk-signal", description="risk evidence", required_stances=["COUNTER"])]),
        ]

    def _qualify(self, record: EvidenceRecord, task: ResearchTask) -> EvidenceRecord:
        requirement = next(item for item in task.evidence_requirements if item.id == record.requirement_id)
        record.qualification = "QUALIFIED" if record.stance in requirement.required_stances else "NEEDS_REVIEW"
        return record

    def _task_is_qualified(self, run: ResearchRun, task: ResearchTask) -> bool:
        for requirement in task.evidence_requirements:
            matching = [
                record for record in run.evidence
                if record.task_id == task.id and record.requirement_id == requirement.id and record.qualification == "QUALIFIED"
            ]
            if len(matching) < requirement.minimum_records:
                return False
        return True

    def _synthesize(self, run: ResearchRun) -> None:
        run.claims = []
        for task in run.tasks:
            evidence = [record for record in run.evidence if record.task_id == task.id and record.qualification == "QUALIFIED"]
            run.claims.append(Claim(task_id=task.id, statement=f"{task.title} produces a material signal for the investment question.", evidence_ids=[item.id for item in evidence], status="QUALIFIED" if evidence else "NEEDS_REVIEW", confidence=0.8 if evidence else 0.2))
        claim_ids = [claim.id for claim in run.claims]
        complete = all(claim.status == "QUALIFIED" for claim in run.claims)
        run.thesis = Thesis(statement="The investment case is evidence-backed but remains contingent on explicit downside conditions.", bull="Operating momentum and market structure improve faster than expected.", base="Current evidence supports a measured thesis with ongoing monitoring.", bear="Counter-evidence compounds and invalidates the key assumptions.", claim_ids=claim_ids, review_status="PENDING_REVIEW" if complete else "NEEDS_REVIEW")

    def _checkpoint(self, run: ResearchRun, completed: set[str]) -> None:
        run.state_version += 1
        payload = {"state_version": run.state_version, "completed_task_ids": sorted(completed), "state_hash": sha256(run.model_dump_json().encode()).hexdigest()}
        checkpoint_id = self.store.save_checkpoint(run.id, payload)
        run.checkpoint = Checkpoint.model_validate({"id": checkpoint_id, "run_id": run.id, **payload})
        self.store.save_run(run.model_dump(mode="json"))
        self.store.append_event(run.id, "CHECKPOINT_SAVED", payload | {"checkpoint_id": checkpoint_id})

    def _persist(self, run: ResearchRun, event_type: str, payload: dict[str, object]) -> None:
        run.updated_at = datetime.now(UTC)
        self.store.save_run(run.model_dump(mode="json"))
        self.store.append_event(run.id, event_type, payload)

    def _fail(self, run: ResearchRun, reason: str) -> ResearchRun:
        run.completed_at = datetime.now(UTC)
        run.state = "FAILED"
        self._persist(run, "RUN_FAILED", {"reason": reason})
        return run
