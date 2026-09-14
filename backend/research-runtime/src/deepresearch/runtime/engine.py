"""Deterministic, dependency-aware research execution."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from hashlib import sha256
from threading import Event, Thread
from uuid import uuid4

from deepresearch.domain.models import (
    Checkpoint,
    Claim,
    DecisionRecord,
    EvaluationResult,
    EvidenceRecord,
    FinancialAnalysisResult,
    InvestmentCommitteeReview,
    InvestmentMemo,
    InvestmentMemory,
    MemoSection,
    RedTeamReview,
    ResearchCase,
    ResearchPlan,
    ResearchRun,
    ResearchTask,
    Thesis,
    ThesisDelta,
    ToolExecution,
    ValuationScenariosResult,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.evidence import EvidenceProvider, EvidenceProviderError, evidence_hash
from deepresearch.runtime.planner import (
    DeterministicResearchPlanner,
    ResearchPlanner,
    research_input_hash,
)
from deepresearch.runtime.synthesis import (
    DeterministicResearchSynthesizer,
    ResearchSynthesizer,
    SynthesisProviderError,
)
from deepresearch.runtime.tools import ResearchToolRegistry


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


class RunLeaseConflictError(RuntimeError):
    """Another executor currently owns the research run."""


class RunLeaseLostError(RuntimeError):
    """The executor lost ownership before it could persist its result."""


class ResearchEngine:
    def __init__(
        self,
        store: SQLiteStore,
        provider: EvidenceProvider,
        planner: ResearchPlanner | None = None,
        synthesizer: ResearchSynthesizer | None = None,
        lease_seconds: float = 300.0,
        tool_registry: ResearchToolRegistry | None = None,
    ) -> None:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        self.store = store
        self.provider = provider
        self.tool_registry = tool_registry or ResearchToolRegistry.from_provider(provider)
        self.planner = planner or DeterministicResearchPlanner()
        self.synthesizer = synthesizer or DeterministicResearchSynthesizer()
        self.lease_seconds = lease_seconds

    def create_run(self, case: ResearchCase, tasks: list[ResearchTask] | None = None) -> ResearchRun:
        plan = self.planner.plan(case) if tasks is None else ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name="explicit-input",
            planner_version="v1",
            input_hash=research_input_hash(case),
            tasks=tasks,
            mandate=case.mandate,
            status="VALIDATED",
        )
        self._validate_plan(plan, case)
        task_list = [ResearchTask.model_validate(task.model_dump()) for task in plan.tasks]
        run = ResearchRun(id=f"run-{uuid4().hex}", case_id=case.id, plan=plan, tasks=task_list)
        self.store.save_case(case.model_dump(mode="json"))
        self.store.save_run(run.model_dump(mode="json"))
        self.store.append_event(run.id, "CASE_CREATED", {"case_id": case.id, "question": case.question})
        self.store.append_event(run.id, "RUN_CREATED", {"task_ids": [task.id for task in task_list]})
        return run

    def get_plan(self, run_id: str) -> ResearchPlan:
        run = self.get_run(run_id)
        if run.plan is None:
            raise KeyError(f"plan missing for {run_id}")
        return run.plan

    def _validate_plan(self, plan: ResearchPlan, case: ResearchCase) -> None:
        validate_task_dag(plan.tasks)
        if plan.case_id != case.id or plan.question != case.question:
            raise ValueError("plan input does not match research case")
        if plan.mandate != case.mandate:
            raise ValueError("plan mandate does not match research case")
        if plan.input_hash != research_input_hash(case):
            raise ValueError("plan input hash does not match research case")
        for task in plan.tasks:
            if not task.evidence_requirements:
                raise ValueError(f"task {task.id} must declare evidence requirements")
        plan.status = "VALIDATED"

    def get_run(self, run_id: str) -> ResearchRun:
        payload = self.store.get_run(run_id)
        if payload is None:
            raise KeyError(run_id)
        return ResearchRun.model_validate(payload)

    def evaluate_run(self, run_id: str, case: dict[str, object]) -> EvaluationResult:
        run = self.get_run(run_id)
        if case.get("case_id") != run.case_id:
            raise ValueError("evaluation case does not match research run")
        from deepresearch.evaluation.scorer import score_run

        result = score_run(run, case).model_copy(update={"run_id": run.id})
        self.store.save_evaluation(result.model_dump(mode="json"))
        self.store.append_event(
            run.id,
            "EVALUATION_RECORDED",
            {"evaluation_id": result.id, "case_hash": result.case_hash, "passed": result.passed},
        )
        return result

    def get_latest_evaluation(self, run_id: str) -> EvaluationResult:
        self.get_run(run_id)
        payload = self.store.latest_evaluation(run_id)
        if payload is None:
            raise KeyError(f"evaluation missing for {run_id}")
        return EvaluationResult.model_validate(payload)

    def list_runs(self, case_id: str) -> list[ResearchRun]:
        return [ResearchRun.model_validate(payload) for payload in self.store.list_runs(case_id)]

    def replan(self, run_id: str) -> ResearchRun:
        run = self.get_run(run_id)
        if run.state != "PARTIAL":
            raise ValueError("only partial runs can be replanned")
        case = self.get_case(run.case_id)
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(run, task, requirement.id)
        ]
        if not unresolved:
            raise ValueError("partial run has no unresolved requirements")
        replan = getattr(self.planner, "replan", None)
        plan = replan(case, unresolved) if callable(replan) else self.planner.plan(case)
        if not plan.tasks:
            raise ValueError("replanner returned no tasks")
        existing_task_ids = {task.id for task in run.tasks}
        if not getattr(self.planner, "supports_dynamic_tasks", False):
            plan = plan.model_copy(update={"tasks": [task for task in plan.tasks if task.id in existing_task_ids]})
            if not plan.tasks:
                raise ValueError("replanner did not retain an existing task")

        reset_task_ids = {item.split(":", 1)[0] for item in unresolved}
        changed = True
        while changed:
            changed = False
            for task in run.tasks:
                if task.id not in reset_task_ids and reset_task_ids.intersection(task.depends_on):
                    reset_task_ids.add(task.id)
                    changed = True
        planned = {task.id: task for task in plan.tasks}
        merged_tasks = []
        for task in run.tasks:
            refreshed = planned.get(task.id, task)
            state = task.state if task.id not in reset_task_ids else "PENDING"
            merged_tasks.append(refreshed.model_copy(update={"state": state}))
        merged_tasks.extend(
            task.model_copy(update={"state": "PENDING"})
            for task in plan.tasks
            if task.id not in existing_task_ids
        )
        merged_plan = plan.model_copy(update={"tasks": merged_tasks})
        self._validate_plan(merged_plan, case)

        run.plan = merged_plan
        run.tasks = merged_tasks
        run.state = "CREATED"
        run.completed_at = None
        run.claims = []
        run.thesis = None
        run.memo = None
        run.checkpoint = None
        run.state_version += 1
        self._persist(
            run,
            "RUN_REPLANNED",
            {
                "unresolved_requirement_ids": unresolved,
                "reset_task_ids": sorted(reset_task_ids),
                "plan_id": plan.id,
            },
        )
        return run

    def get_case(self, case_id: str) -> ResearchCase:
        payload = self.store.get_case(case_id)
        if payload is None:
            raise KeyError(case_id)
        return ResearchCase.model_validate(payload)

    def list_cases(self) -> list[ResearchCase]:
        return [ResearchCase.model_validate(payload) for payload in self.store.list_cases()]

    def trace(self, run_id: str) -> dict[str, object]:
        run = self.get_run(run_id)
        evidence_by_id = {record.id: record for record in run.evidence}
        requirements_by_task = {
            task.id: {requirement.id: requirement for requirement in task.evidence_requirements}
            for task in run.tasks
        }
        missing_requirements: dict[str, list[str]] = {}
        for task_id, requirements in requirements_by_task.items():
            missing = []
            for requirement_id, requirement in requirements.items():
                qualified = sum(
                    record.qualification == "QUALIFIED"
                    for record in run.evidence
                    if record.task_id == task_id and record.requirement_id == requirement_id
                )
                if qualified < requirement.minimum_records:
                    missing.append(requirement_id)
            if missing:
                missing_requirements[task_id] = missing
        by_qualification = {
            qualification: sum(record.qualification == qualification for record in run.evidence)
            for qualification in ("QUALIFIED", "NEEDS_REVIEW", "UNQUALIFIED")
        }
        provenance_complete = sum(record.provenance_complete for record in run.evidence)
        return {
            "run_id": run.id,
            "case_id": run.case_id,
            "state": run.state,
            "tasks": [
                {
                    "id": task.id,
                    "state": task.state,
                    "depends_on": task.depends_on,
                    "missing_requirement_ids": missing_requirements.get(task.id, []),
                }
                for task in run.tasks
            ],
            "evidence": {
                "total": len(run.evidence),
                "by_qualification": by_qualification,
                "provenance_complete": provenance_complete,
                "provenance_incomplete": len(run.evidence) - provenance_complete,
            },
            "claims": [
                {
                    "id": claim.id,
                    "task_id": claim.task_id,
                    "status": claim.status,
                    "evidence_ids": claim.evidence_ids,
                    "unresolved_evidence_ids": [item for item in claim.evidence_ids if item not in evidence_by_id],
                }
                for claim in run.claims
            ],
        }

    def execute(self, run_id: str, stop_after_tasks: int | None = None) -> ResearchRun:
        current = self.get_run(run_id)
        if current.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"}:
            return current
        lease_id = f"lease-{uuid4().hex}"
        if not self.store.acquire_run_lease(run_id, lease_id, self.lease_seconds):
            raise RunLeaseConflictError(f"research run {run_id} is already being executed")
        heartbeat_stop = Event()
        heartbeat_lost = Event()
        heartbeat = Thread(
            target=self._heartbeat,
            args=(run_id, lease_id, heartbeat_stop, heartbeat_lost),
            daemon=True,
        )
        heartbeat.start()
        try:
            self.store.append_event(run_id, "RUN_LEASE_ACQUIRED", {"lease_id": lease_id})
            return self._execute(run_id, stop_after_tasks, lease_id, heartbeat_lost)
        finally:
            heartbeat_stop.set()
            heartbeat.join(timeout=min(max(self.lease_seconds / 3, 0.05), 1.0))
            released = self.store.release_run_lease(run_id, lease_id)
            self.store.append_event(
                run_id,
                "RUN_LEASE_RELEASED",
                {"lease_id": lease_id, "released": released, "heartbeat_lost": heartbeat_lost.is_set()},
            )

    def _heartbeat(self, run_id: str, lease_id: str, stop: Event, lost: Event) -> None:
        interval = min(max(self.lease_seconds / 3, 0.01), 30.0)
        while not stop.wait(interval):
            try:
                renewed = self.store.renew_run_lease(run_id, lease_id, self.lease_seconds)
            except Exception:
                renewed = False
            if not renewed:
                lost.set()
                return

    def resolve_tool_attempt(self, run_id: str, attempt_id: str, action: str) -> ResearchRun:
        run = self.get_run(run_id)
        if run.state != "BLOCKED":
            raise ValueError("only blocked runs can resolve a tool attempt")
        attempt = next((item for item in run.tool_executions if item.id == attempt_id), None)
        if attempt is None or attempt.status != "UNKNOWN_EFFECT" or attempt.completed_at is not None:
            raise ValueError("unknown in-flight tool attempt not found")
        task = next((item for item in run.tasks if item.id == attempt.task_id), None)
        if task is None or task.state != "UNKNOWN_EFFECT":
            raise ValueError("unknown tool attempt task not found")
        if action == "RETRY":
            task.state = "PENDING"
            run.state = "CREATED"
            run.completed_at = None
            event_type = "TOOL_ATTEMPT_RETRY_AUTHORIZED"
            attempt.resolution = "RETRY_AUTHORIZED"
        elif action == "MARK_FAILED":
            task.state = "FAILED"
            run.completed_at = datetime.now(UTC)
            run.state = "FAILED"
            event_type = "TOOL_ATTEMPT_MARKED_FAILED"
            attempt.resolution = "MARKED_FAILED"
        else:
            raise ValueError("action must be RETRY or MARK_FAILED")
        attempt.completed_at = datetime.now(UTC)
        attempt.error_type = "Resolved"
        attempt.error_message = f"Operator resolution: {action}"
        self._persist(run, event_type, {"attempt_id": attempt.id, "action": action})
        return run

    def _execute(
        self,
        run_id: str,
        stop_after_tasks: int | None = None,
        lease_id: str | None = None,
        heartbeat_lost: Event | None = None,
    ) -> ResearchRun:
        self._ensure_lease(heartbeat_lost)
        run = self.get_run(run_id)
        if run.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"}:
            return run
        case = self.get_case(run.case_id)
        abandoned = [task for task in run.tasks if task.state == "RUNNING"]
        for task in abandoned:
            provider_name = self._provider_name(task.tool_name)
            unfinished = next(
                (
                    execution
                    for execution in reversed(run.tool_executions)
                    if execution.task_id == task.id
                    and execution.status == "UNKNOWN_EFFECT"
                    and execution.completed_at is None
                ),
                None,
            )
            if unfinished is None:
                attempt_key = f"{run.id}:{task.id}:legacy-recovery"
                unfinished = ToolExecution(
                    task_id=task.id,
                    tool_name=task.tool_name,
                    provider=provider_name,
                    input_hash=self._task_input_hash(case, task),
                    status="UNKNOWN_EFFECT",
                    attempt_key=attempt_key,
                    result_hash=sha256(attempt_key.encode()).hexdigest(),
                    completed_at=None,
                    error_type="LegacyRecovery",
                    error_message="Task was RUNNING without a durable attempt receipt.",
                    error_hash=sha256(attempt_key.encode()).hexdigest(),
                )
                run.tool_executions.append(unfinished)
            task.state = "UNKNOWN_EFFECT"
            run.state = "BLOCKED"
            self._persist(
                run,
                "TOOL_ATTEMPT_UNKNOWN_EFFECT",
                {"task_id": task.id, "attempt_id": unfinished.id, "attempt_key": unfinished.attempt_key},
                lease_id,
            )
            return run
        completed = {task.id for task in run.tasks if task.state == "COMPLETED"}
        if completed:
            self._append_event(run.id, "RUN_RESUMED", {"completed_task_ids": sorted(completed)}, lease_id)
        executed_this_call = 0
        while len(completed) < len(run.tasks):
            self._ensure_lease(heartbeat_lost)
            ready = [
                task for task in run.tasks if task.state == "PENDING" and set(task.depends_on) <= completed
            ]
            if not ready:
                return self._fail(run, "no ready task; DAG is inconsistent", lease_id)
            for task in sorted(ready, key=lambda item: item.id):
                self._ensure_lease(heartbeat_lost)
                provider_name = self._provider_name(task.tool_name)
                task.state = "RUNNING"
                run.state = "RUNNING"
                self._persist(run, "TASK_STARTED", {"task_id": task.id}, lease_id)
                tool_started_at = datetime.now(UTC)
                attempt_key = f"{run.id}:{task.id}:attempt-{sum(item.task_id == task.id for item in run.tool_executions) + 1}"
                attempt_hash = sha256(attempt_key.encode()).hexdigest()
                attempt = ToolExecution(
                    task_id=task.id,
                    tool_name=task.tool_name,
                    provider=provider_name,
                    input_hash=self._task_input_hash(case, task),
                    status="UNKNOWN_EFFECT",
                    attempt_key=attempt_key,
                    result_hash=attempt_hash,
                    started_at=tool_started_at,
                    completed_at=None,
                    error_type="InFlight",
                    error_message="Provider result has not been acknowledged.",
                    error_hash=attempt_hash,
                )
                run.tool_executions.append(attempt)
                self._persist(
                    run,
                    "TOOL_ATTEMPT_STARTED",
                    {"task_id": task.id, "attempt_id": attempt.id, "attempt_key": attempt_key},
                    lease_id,
                )
                try:
                    records = self.tool_registry.collect(task, case)
                except Exception as error:
                    self._ensure_lease(heartbeat_lost)
                    diagnostic = f"{type(error).__name__}:{error}"
                    diagnostic_hash = sha256(diagnostic.encode()).hexdigest()
                    attempt.status = "FAILED"
                    attempt.result_hash = diagnostic_hash
                    attempt.completed_at = datetime.now(UTC)
                    attempt.error_type = type(error).__name__
                    attempt.error_message = str(error)[:1000]
                    attempt.error_hash = diagnostic_hash
                    task.state = "FAILED"
                    return self._fail(
                        run,
                        f"evidence provider failed for task {task.id}: {type(error).__name__}: {error}",
                        lease_id,
                    )
                self._ensure_lease(heartbeat_lost)
                qualified = [self._qualify(record, task) for record in records]
                attempt.evidence_count = len(qualified)
                attempt.qualified_evidence_count = sum(record.qualification == "QUALIFIED" for record in qualified)
                attempt.review_evidence_count = sum(record.qualification == "NEEDS_REVIEW" for record in qualified)
                attempt.unqualified_evidence_count = sum(record.qualification == "UNQUALIFIED" for record in qualified)
                existing_evidence = {
                    (record.id, record.content_hash): index for index, record in enumerate(run.evidence)
                }
                pending_evidence: dict[tuple[str, str | None], int] = {}
                new_evidence: list[EvidenceRecord] = []
                for record in qualified:
                    key = (record.id, record.content_hash)
                    if key in pending_evidence:
                        pending_index = pending_evidence[key]
                        if new_evidence[pending_index].qualification != record.qualification:
                            new_evidence[pending_index] = record
                    elif key not in existing_evidence:
                        pending_evidence[key] = len(new_evidence)
                        new_evidence.append(record)
                    elif run.evidence[existing_evidence[key]].qualification != record.qualification:
                        run.evidence[existing_evidence[key]] = record
                run.evidence.extend(new_evidence)
                result_hash = evidence_hash(qualified) if qualified else sha256(b"empty").hexdigest()
                attempt.status = "SUCCEEDED"
                attempt.result_hash = result_hash
                attempt.completed_at = datetime.now(UTC)
                attempt.error_type = None
                attempt.error_message = None
                attempt.error_hash = None
                task.state = "COMPLETED"
                completed.add(task.id)
                executed_this_call += 1
                self._persist(run, "TASK_COMPLETED", {"task_id": task.id, "evidence_count": len(new_evidence)}, lease_id)
                self._checkpoint(run, completed, lease_id)
                if stop_after_tasks is not None and executed_this_call >= stop_after_tasks:
                    return run
        self._ensure_lease(heartbeat_lost)
        run.state = "VERIFYING"
        self._persist(run, "RUN_VERIFYING", {}, lease_id)
        try:
            self._synthesize(run, case, lease_id, heartbeat_lost)
        except (EvidenceProviderError, SynthesisProviderError) as error:
            self._ensure_lease(heartbeat_lost)
            return self._fail(run, f"claim verification failed: {error}", lease_id)
        self._ensure_lease(heartbeat_lost)
        run.completed_at = datetime.now(UTC)
        run.state = (
            "COMPLETED"
            if all(self._task_is_qualified(run, task) for task in run.tasks)
            and all(claim.status == "QUALIFIED" for claim in run.claims)
            else "PARTIAL"
        )
        memory = self._build_memo(run, case.target)
        self._persist(
            run,
            "RUN_COMPLETED" if run.state == "COMPLETED" else "RUN_PARTIAL",
            {"claim_count": len(run.claims)},
            lease_id,
        )
        memory_payload = memory.model_dump(mode="json")
        if lease_id:
            if not self.store.save_memory_owned(memory_payload, run.id, lease_id):
                raise RunLeaseLostError(f"research run {run.id} lease ownership was lost")
        else:
            self.store.save_memory(memory_payload)
        return run

    def cancel(self, run_id: str, reason: str) -> ResearchRun:
        run = self.get_run(run_id)
        if run.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED", "BLOCKED"}:
            return run
        run.completed_at = datetime.now(UTC)
        run.state = "CANCELLED"
        self._persist(run, "RUN_CANCELLED", {"reason": reason})
        return run

    def record_decision(self, run_id: str, decision: DecisionRecord) -> ResearchRun:
        run = self.get_run(run_id)
        if decision.target_id != (run.thesis.id if run.thesis else decision.target_id):
            raise ValueError("decision target does not belong to this run")
        if decision.review_ids:
            reviews = {review.id: review for review in run.ic_reviews}
            missing_reviews = sorted(set(decision.review_ids) - reviews.keys())
            if missing_reviews:
                raise ValueError(f"decision review not found in run: {missing_reviews}")
            if run.thesis is not None:
                invalid_reviews = sorted(
                    review_id for review_id in set(decision.review_ids) if reviews[review_id].thesis_id != run.thesis.id
                )
                if invalid_reviews:
                    raise ValueError(f"decision review does not belong to current thesis: {invalid_reviews}")
        if decision.action == "APPROVE_THESIS":
            if run.thesis is None or run.state != "COMPLETED":
                raise ValueError("only a completed run can approve a thesis")
            run.thesis.review_status = "APPROVED"
            if run.memo is not None:
                run.memo.status = "APPROVED"
        elif decision.action == "REJECT_THESIS" and run.thesis is not None:
            run.thesis.review_status = "NEEDS_REVIEW"
            if run.memo is not None:
                run.memo.status = "READY_FOR_REVIEW" if run.state == "COMPLETED" else "DRAFT"
        run.decisions.append(decision)
        case = self.get_case(run.case_id)
        memory_payload = self.store.get_memory(case.target)
        if memory_payload is not None:
            memory = InvestmentMemory.model_validate(memory_payload)
            if decision.id not in memory.decision_ids:
                memory.decision_ids.append(decision.id)
                memory.updated_at = datetime.now(UTC)
                self.store.save_memory(memory.model_dump(mode="json"))
        self._persist(run, "HUMAN_DECISION", decision.model_dump(mode="json"))
        return run

    def record_red_team_review(self, run_id: str, review: RedTeamReview) -> ResearchRun:
        run = self.get_run(run_id)
        if run.thesis is None:
            raise ValueError("red-team review requires a synthesized thesis")
        if review.run_id != run.id or review.thesis_id != run.thesis.id:
            raise ValueError("red-team review target does not belong to this run")
        records = {record.id: record for record in run.evidence}
        missing = sorted(set(review.evidence_ids) - records.keys())
        if missing:
            raise ValueError(f"red-team evidence not found in run: {missing}")
        invalid_stance = sorted(
            evidence_id
            for evidence_id in set(review.evidence_ids)
            if records[evidence_id].stance not in {"COUNTER", "CONFLICTING"}
        )
        if invalid_stance:
            raise ValueError(f"red-team evidence must be counter or conflicting: {invalid_stance}")
        if any(item.id == review.id for item in run.red_team_reviews):
            raise ValueError(f"red-team review already exists: {review.id}")
        run.red_team_reviews.append(review)
        if run.memo is not None:
            run.memo.red_team_review_ids.append(review.id)
        if review.outcome == "REQUIRES_RESEARCH":
            run.thesis.review_status = "NEEDS_REVIEW"
            if run.memo is not None:
                run.memo.status = "READY_FOR_REVIEW" if run.state == "COMPLETED" else "DRAFT"
        self._persist(
            run,
            "RED_TEAM_REVIEW_RECORDED",
            {
                "review_id": review.id,
                "thesis_id": review.thesis_id,
                "outcome": review.outcome,
                "evidence_ids": review.evidence_ids,
            },
        )
        return run

    def get_red_team_reviews(self, run_id: str) -> list[RedTeamReview]:
        return self.get_run(run_id).red_team_reviews

    def record_ic_review(self, run_id: str, review: InvestmentCommitteeReview) -> ResearchRun:
        run = self.get_run(run_id)
        if run.thesis is None:
            raise ValueError("IC review requires a synthesized thesis")
        if review.run_id != run.id or review.thesis_id != run.thesis.id:
            raise ValueError("IC review target does not belong to this run")
        records = {record.id: record for record in run.evidence}
        missing = sorted(set(review.evidence_ids) - records.keys())
        if missing:
            raise ValueError(f"IC review evidence not found in run: {missing}")
        if any(item.id == review.id for item in run.ic_reviews):
            raise ValueError(f"IC review already exists: {review.id}")
        run.ic_reviews.append(review)
        if run.memo is not None:
            run.memo.ic_review_ids.append(review.id)
        self._persist(
            run,
            "IC_REVIEW_RECORDED",
            {
                "review_id": review.id,
                "thesis_id": review.thesis_id,
                "role": review.role,
                "position": review.position,
                "recommendation": review.recommendation,
                "evidence_ids": review.evidence_ids,
            },
        )
        return run

    def get_ic_reviews(self, run_id: str) -> list[InvestmentCommitteeReview]:
        return self.get_run(run_id).ic_reviews

    def get_memo(self, run_id: str) -> InvestmentMemo:
        run = self.get_run(run_id)
        if run.memo is None:
            raise KeyError(f"memo missing for {run_id}")
        return run.memo

    def get_financial_analysis(self, run_id: str) -> FinancialAnalysisResult:
        run = self.get_run(run_id)
        if run.financial_analysis is None:
            raise KeyError(f"financial analysis missing for {run_id}")
        return run.financial_analysis

    def get_valuation_scenarios(self, run_id: str) -> ValuationScenariosResult:
        run = self.get_run(run_id)
        if run.valuation_scenarios is None:
            raise KeyError(f"valuation scenarios missing for {run_id}")
        return run.valuation_scenarios

    def record_financial_analysis(self, run_id: str, analysis: FinancialAnalysisResult) -> ResearchRun:
        run = self.get_run(run_id)
        records = {record.id: record for record in run.evidence}
        requested_ids = {evidence_id for ids in analysis.evidence_ids.values() for evidence_id in ids}
        missing = sorted(requested_ids - records.keys())
        if missing:
            raise ValueError(f"financial evidence not found in run: {missing}")
        unqualified = sorted(
            evidence_id for evidence_id in requested_ids if records[evidence_id].qualification != "QUALIFIED"
        )
        if unqualified:
            raise ValueError(f"financial evidence is not qualified: {unqualified}")
        run.financial_analysis = analysis
        if run.memo is not None:
            run.memo.financial_analysis_input_hash = analysis.input_hash
        self._persist(
            run,
            "FINANCIAL_ANALYSIS_RECORDED",
            {
                "period": analysis.period,
                "input_hash": analysis.input_hash,
                "evidence_ids": analysis.evidence_ids,
            },
        )
        return run

    def record_valuation_scenarios(self, run_id: str, result: ValuationScenariosResult) -> ResearchRun:
        run = self.get_run(run_id)
        if result.run_id != run.id or result.case_id != run.case_id:
            raise ValueError("valuation scenario artifact target does not belong to this run")
        requested_ids = set(result.base_revenue_evidence_ids)
        for scenario in result.scenarios:
            requested_ids.update(
                evidence_id
                for evidence_ids in scenario.assumptions.evidence_ids.values()
                for evidence_id in evidence_ids
            )
        records = {record.id: record for record in run.evidence}
        missing = sorted(requested_ids - records.keys())
        if missing:
            raise ValueError(f"valuation evidence not found in run: {missing}")
        unqualified = sorted(
            evidence_id for evidence_id in requested_ids if records[evidence_id].qualification != "QUALIFIED"
        )
        if unqualified:
            raise ValueError(f"valuation evidence is not qualified: {unqualified}")
        run.valuation_scenarios = result
        if run.memo is not None:
            run.memo.valuation_scenarios_id = result.id
        self._persist(
            run,
            "VALUATION_SCENARIOS_RECORDED",
            {
                "artifact_id": result.id,
                "input_hash": result.input_hash,
                "scenario_names": [scenario.scenario for scenario in result.scenarios],
                "evidence_ids": sorted(requested_ids),
            },
        )
        return run

    def get_memory(self, target: str) -> InvestmentMemory:
        payload = self.store.get_memory(target)
        if payload is None:
            raise KeyError(target)
        return InvestmentMemory.model_validate(payload)

    def get_memory_for_run(self, run_id: str) -> InvestmentMemory:
        run = self.get_run(run_id)
        case = self.get_case(run.case_id)
        return self.get_memory(case.target)

    def _qualify(self, record: EvidenceRecord, task: ResearchTask) -> EvidenceRecord:
        provider = self.tool_registry.resolve(task.tool_name)
        if getattr(provider, "qualification_authority", "runtime") == "external":
            return record
        requirement = next(item for item in task.evidence_requirements if item.id == record.requirement_id)
        record.qualification = (
            "QUALIFIED"
            if record.provenance_complete and record.stance in requirement.required_stances
            else "NEEDS_REVIEW"
        )
        return record

    def _task_is_qualified(self, run: ResearchRun, task: ResearchTask) -> bool:
        for requirement in task.evidence_requirements:
            matching = {
                record.id
                for record in run.evidence
                if record.task_id == task.id
                and record.requirement_id == requirement.id
                and record.qualification == "QUALIFIED"
            }
            if len(matching) < requirement.minimum_records:
                return False
        return True

    def _synthesize(
        self,
        run: ResearchRun,
        case: ResearchCase,
        lease_id: str | None = None,
        heartbeat_lost: Event | None = None,
    ) -> None:
        draft = self.synthesizer.synthesize(case, run)
        tasks_by_id = {task.id: task for task in run.tasks}
        evidence_by_id = {record.id: record for record in run.evidence}
        if {claim.task_id for claim in draft.claims} != set(tasks_by_id) or len(draft.claims) != len(tasks_by_id):
            raise SynthesisProviderError("synthesis must return exactly one claim for every research task")
        run.claims = []
        for proposed in draft.claims:
            if proposed.task_id not in tasks_by_id:
                raise SynthesisProviderError(f"synthesis claim references unknown task: {proposed.task_id}")
            evidence_ids = list(dict.fromkeys(proposed.evidence_ids))
            missing = sorted(set(evidence_ids) - evidence_by_id.keys())
            if missing:
                raise SynthesisProviderError(f"synthesis claim references unknown evidence: {missing}")
            unqualified = sorted(
                evidence_id for evidence_id in evidence_ids if evidence_by_id[evidence_id].qualification != "QUALIFIED"
            )
            if unqualified:
                raise SynthesisProviderError(f"synthesis claim references unqualified evidence: {unqualified}")
            claim = Claim(
                task_id=proposed.task_id,
                statement=proposed.statement,
                evidence_ids=evidence_ids,
                status="QUALIFIED" if evidence_ids and self._task_is_qualified(run, tasks_by_id[proposed.task_id]) else "NEEDS_REVIEW",
                confidence=proposed.confidence,
            )
            provider = self.tool_registry.resolve(tasks_by_id[claim.task_id].tool_name)
            verify_claim = getattr(provider, "verify_claim", None)
            if claim.status == "QUALIFIED" and callable(verify_claim):
                attempt_key = f"{run.id}:claim-verification:{claim.id}:attempt-1"
                attempt_hash = sha256(attempt_key.encode()).hexdigest()
                verification = ToolExecution(
                    task_id=claim.task_id,
                    tool_name="claim-verification",
                    provider=str(getattr(provider, "name", provider.__class__.__name__)),
                    input_hash=self._claim_input_hash(claim.statement, claim.evidence_ids),
                    operation="CLAIM_VERIFICATION",
                    status="UNKNOWN_EFFECT",
                    attempt_key=attempt_key,
                    result_hash=attempt_hash,
                    completed_at=None,
                    error_type="InFlight",
                    error_message="Claim verification result has not been acknowledged.",
                    error_hash=attempt_hash,
                )
                run.tool_executions.append(verification)
                self._ensure_lease(heartbeat_lost)
                self._persist(
                    run,
                    "CLAIM_VERIFICATION_STARTED",
                    {"claim_id": claim.id, "attempt_id": verification.id, "attempt_key": attempt_key},
                    lease_id,
                )
                try:
                    provider_result = verify_claim(claim.statement, claim.evidence_ids)
                    if not isinstance(provider_result, bool):
                        raise EvidenceProviderError("claim verification provider must return bool")
                    supported = provider_result
                except Exception as error:
                    self._ensure_lease(heartbeat_lost)
                    diagnostic = f"{type(error).__name__}:{error}"
                    diagnostic_hash = sha256(diagnostic.encode()).hexdigest()
                    verification.status = "FAILED"
                    verification.result_hash = diagnostic_hash
                    verification.completed_at = datetime.now(UTC)
                    verification.error_type = type(error).__name__
                    verification.error_message = str(error)[:1000]
                    verification.error_hash = diagnostic_hash
                    self._persist(
                        run,
                        "CLAIM_VERIFICATION_FAILED",
                        {"claim_id": claim.id, "attempt_id": verification.id, "error_hash": diagnostic_hash},
                        lease_id,
                    )
                    raise EvidenceProviderError(f"claim verification failed: {error}") from error
                self._ensure_lease(heartbeat_lost)
                verification.status = "SUCCEEDED"
                verification.verification_supported = supported
                verification.result_hash = sha256(f"{verification.input_hash}:{supported}".encode()).hexdigest()
                verification.completed_at = datetime.now(UTC)
                verification.error_type = None
                verification.error_message = None
                verification.error_hash = None
                self._persist(
                    run,
                    "CLAIM_VERIFICATION_COMPLETED",
                    {"claim_id": claim.id, "attempt_id": verification.id, "supported": supported},
                    lease_id,
                )
                if not supported:
                    claim.status = "NEEDS_REVIEW"
            run.claims.append(claim)
        claim_ids = [claim.id for claim in run.claims]
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(run, task, requirement.id)
        ]
        run.thesis = Thesis(
            statement=draft.thesis.statement,
            bull=draft.thesis.bull,
            base=draft.thesis.base,
            bear=draft.thesis.bear,
            claim_ids=claim_ids,
            review_status="PENDING_REVIEW" if not unresolved else "NEEDS_REVIEW",
            provenance=draft.provenance,
        )

    def _requirement_is_qualified(self, run: ResearchRun, task: ResearchTask, requirement_id: str) -> bool:
        requirement = next(item for item in task.evidence_requirements if item.id == requirement_id)
        return len({
            record.id
            for record in run.evidence
            if record.task_id == task.id
            and record.requirement_id == requirement_id
            and record.qualification == "QUALIFIED"
        }) >= requirement.minimum_records

    def _build_memo(self, run: ResearchRun, target: str) -> InvestmentMemory:
        if run.thesis is None:
            raise ValueError("cannot build a memo without a thesis")
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(run, task, requirement.id)
        ]
        qualified_evidence_ids = [
            record.id for record in run.evidence if record.qualification == "QUALIFIED"
        ]
        counter_evidence_ids = [
            record.id
            for record in run.evidence
            if record.stance in {"COUNTER", "CONFLICTING"}
        ]
        sections = self._build_memo_sections(
            run, qualified_evidence_ids, counter_evidence_ids, unresolved
        )
        run.memo = InvestmentMemo(
            run_id=run.id,
            case_id=run.case_id,
            title=f"Research memo for {run.case_id}",
            status="READY_FOR_REVIEW" if run.state == "COMPLETED" else "DRAFT",
            executive_summary=(
                f"Observed evidence qualified {len(qualified_evidence_ids)} records across "
                f"{len(run.tasks)} task claims; unresolved requirements: {', '.join(unresolved) or 'none'}. "
                "This memo is a review artifact, not a trade instruction."
            ),
            thesis_id=run.thesis.id,
            claim_ids=[claim.id for claim in run.claims],
            evidence_ids=list(dict.fromkeys(qualified_evidence_ids)),
            counter_evidence_ids=list(dict.fromkeys(counter_evidence_ids)),
            unresolved_requirement_ids=unresolved,
            sections=sections,
            provenance={
                "generator": "deterministic-evidence-synthesis",
                "run_state": run.state,
            },
        )
        previous = self.store.get_memory(target)
        memory = InvestmentMemory.model_validate(previous) if previous is not None else None
        previous_run = None
        if memory is not None:
            previous_payload = self.store.get_run(memory.latest_run_id)
            if previous_payload is not None:
                try:
                    previous_run = ResearchRun.model_validate(previous_payload)
                except ValueError:
                    previous_run = None
        run_thesis_id = run.thesis.id
        if memory is None:
            memory = InvestmentMemory(
                target=target,
                latest_run_id=run.id,
                latest_thesis_id=run_thesis_id,
            )
        else:
            memory.previous_thesis_id = memory.latest_thesis_id
            memory.latest_run_id = run.id
            memory.latest_thesis_id = run_thesis_id
        memory.case_ids.append(run.case_id)
        memory.run_ids.append(run.id)
        memory.memo_ids.append(run.memo.id)
        memory.thesis_ids.append(run_thesis_id)
        memory.latest_thesis_delta = self._thesis_delta(previous_run, run, memory)
        memory.unresolved_requirement_ids = unresolved
        memory.updated_at = datetime.now(UTC)
        return memory

    def _build_memo_sections(
        self,
        run: ResearchRun,
        qualified_evidence_ids: list[str],
        counter_evidence_ids: list[str],
        unresolved: list[str],
    ) -> list[MemoSection]:
        if run.thesis is None:
            raise ValueError("cannot build memo sections without a thesis")
        claim_ids = [claim.id for claim in run.claims]
        evidence_count = len(run.evidence)
        support = "none" if not qualified_evidence_ids else str(len(qualified_evidence_ids))
        unresolved_text = ", ".join(unresolved) or "none"
        return [
            MemoSection(
                section_key="thesis",
                title="Investment thesis",
                body=run.thesis.statement,
                claim_ids=list(run.thesis.claim_ids),
                evidence_ids=list(dict.fromkeys(qualified_evidence_ids)),
                unresolved_requirement_ids=list(unresolved),
            ),
            MemoSection(
                section_key="evidence",
                title="Evidence coverage",
                body=(
                    f"Observed {evidence_count} evidence records; {support} are qualified. "
                    f"Unresolved requirements: {unresolved_text}."
                ),
                claim_ids=claim_ids,
                evidence_ids=[record.id for record in run.evidence],
                unresolved_requirement_ids=list(unresolved),
            ),
            MemoSection(
                section_key="risks",
                title="Risks and disconfirming conditions",
                body=run.thesis.bear,
                claim_ids=claim_ids,
                evidence_ids=list(dict.fromkeys(counter_evidence_ids)),
                unresolved_requirement_ids=list(unresolved),
            ),
            MemoSection(
                section_key="scenarios",
                title="Bull / base / bear scenarios",
                body=(
                    f"Bull: {run.thesis.bull}\nBase: {run.thesis.base}\nBear: {run.thesis.bear}"
                ),
                claim_ids=list(run.thesis.claim_ids),
                evidence_ids=list(dict.fromkeys(qualified_evidence_ids)),
                unresolved_requirement_ids=list(unresolved),
            ),
            MemoSection(
                section_key="decision",
                title="Decision readiness",
                body=(
                    "Ready for human review; no unresolved evidence requirements remain."
                    if not unresolved
                    else f"Human review required before approval. Unresolved requirements: {unresolved_text}."
                ),
                claim_ids=list(run.thesis.claim_ids),
                evidence_ids=list(dict.fromkeys(qualified_evidence_ids + counter_evidence_ids)),
                unresolved_requirement_ids=list(unresolved),
            ),
        ]

    def _thesis_delta(
        self,
        previous_run: ResearchRun | None,
        current_run: ResearchRun,
        previous_memory: InvestmentMemory,
    ) -> ThesisDelta | None:
        if previous_run is None or previous_run.thesis is None or current_run.thesis is None:
            return None
        previous_counter = sum(
            record.stance in {"COUNTER", "CONFLICTING"} for record in previous_run.evidence
        )
        current_counter = sum(
            record.stance in {"COUNTER", "CONFLICTING"} for record in current_run.evidence
        )
        previous_qualified = sum(record.qualification == "QUALIFIED" for record in previous_run.evidence)
        current_qualified = sum(record.qualification == "QUALIFIED" for record in current_run.evidence)
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in current_run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(current_run, task, requirement.id)
        ]
        return ThesisDelta(
            previous_thesis_id=previous_run.thesis.id,
            current_thesis_id=current_run.thesis.id,
            qualified_evidence_delta=current_qualified - previous_qualified,
            counter_conflicting_evidence_delta=current_counter - previous_counter,
            unresolved_requirement_delta=len(unresolved) - len(previous_memory.unresolved_requirement_ids),
            summary=(
                "Observed count change: "
                f"qualified_evidence={current_qualified - previous_qualified:+d}, "
                f"counter_conflicting_evidence={current_counter - previous_counter:+d}, "
                f"unresolved_requirements={len(unresolved) - len(previous_memory.unresolved_requirement_ids):+d}. "
                "This is not a confidence estimate or investment advice."
            ),
        )

    def _checkpoint(self, run: ResearchRun, completed: set[str], lease_id: str | None = None) -> None:
        run.state_version += 1
        payload = {"state_version": run.state_version, "completed_task_ids": sorted(completed), "state_hash": sha256(run.model_dump_json().encode()).hexdigest()}
        checkpoint_id = (
            self.store.save_checkpoint_owned(run.id, lease_id, payload)
            if lease_id
            else self.store.save_checkpoint(run.id, payload)
        )
        if checkpoint_id is None:
            raise RunLeaseLostError(f"research run {run.id} lease ownership was lost")
        run.checkpoint = Checkpoint.model_validate({"id": checkpoint_id, "run_id": run.id, **payload})
        self._persist(run, "CHECKPOINT_SAVED", payload | {"checkpoint_id": checkpoint_id}, lease_id)

    def _persist(
        self,
        run: ResearchRun,
        event_type: str,
        payload: dict[str, object],
        lease_id: str | None = None,
    ) -> None:
        run.updated_at = datetime.now(UTC)
        serialized = run.model_dump(mode="json")
        if lease_id:
            if not self.store.save_run_owned(serialized, lease_id):
                raise RunLeaseLostError(f"research run {run.id} lease ownership was lost")
            if not self.store.append_event_owned(run.id, lease_id, event_type, payload):
                raise RunLeaseLostError(f"research run {run.id} lease ownership was lost")
        else:
            self.store.save_run(serialized)
            self.store.append_event(run.id, event_type, payload)

    def _fail(self, run: ResearchRun, reason: str, lease_id: str | None = None) -> ResearchRun:
        run.completed_at = datetime.now(UTC)
        run.state = "FAILED"
        self._persist(run, "RUN_FAILED", {"reason": reason}, lease_id)
        return run

    @staticmethod
    def _ensure_lease(heartbeat_lost: Event | None) -> None:
        if heartbeat_lost is not None and heartbeat_lost.is_set():
            raise RunLeaseLostError("research run lease ownership was lost")

    @staticmethod
    def _task_input_hash(case: ResearchCase, task: ResearchTask) -> str:
        case_input = case.model_dump_json(exclude={"created_at"})
        task_input = task.model_dump_json(exclude={"state"})
        return sha256(f"{case_input}:{task_input}".encode()).hexdigest()

    def _provider_name(self, tool_name: str) -> str:
        provider = self.tool_registry.get(tool_name)
        return str(getattr(provider, "name", provider.__class__.__name__)) if provider is not None else "unregistered"

    @staticmethod
    def _claim_input_hash(statement: str, evidence_ids: list[str]) -> str:
        evidence_input = "\0".join(evidence_ids)
        return sha256(f"{statement}\0{evidence_input}".encode()).hexdigest()

    def _append_event(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, object],
        lease_id: str | None = None,
    ) -> None:
        if lease_id:
            if not self.store.append_event_owned(run_id, lease_id, event_type, payload):
                raise RunLeaseLostError(f"research run {run_id} lease ownership was lost")
        else:
            self.store.append_event(run_id, event_type, payload)
