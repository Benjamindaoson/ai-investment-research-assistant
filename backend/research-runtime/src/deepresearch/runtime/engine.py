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
    EvidenceRecord,
    FinancialAnalysisResult,
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
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.evidence import EvidenceProvider, EvidenceProviderError, evidence_hash
from deepresearch.runtime.planner import (
    DeterministicResearchPlanner,
    ResearchPlanner,
    research_input_hash,
)


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
    def __init__(self, store: SQLiteStore, provider: EvidenceProvider, planner: ResearchPlanner | None = None, lease_seconds: float = 300.0) -> None:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        self.store = store
        self.provider = provider
        self.planner = planner or DeterministicResearchPlanner()
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
        if current.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"}:
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

    def _execute(
        self,
        run_id: str,
        stop_after_tasks: int | None = None,
        lease_id: str | None = None,
        heartbeat_lost: Event | None = None,
    ) -> ResearchRun:
        self._ensure_lease(heartbeat_lost)
        run = self.get_run(run_id)
        if run.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"}:
            return run
        case = self.get_case(run.case_id)
        abandoned = [task for task in run.tasks if task.state == "RUNNING"]
        for task in abandoned:
            task.state = "PENDING"
            self._persist(run, "TASK_RECOVERED", {"task_id": task.id}, lease_id)
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
                task.state = "RUNNING"
                run.state = "RUNNING"
                self._persist(run, "TASK_STARTED", {"task_id": task.id}, lease_id)
                tool_started_at = datetime.now(UTC)
                try:
                    records = self.provider.collect(task, case)
                except Exception as error:
                    self._ensure_lease(heartbeat_lost)
                    diagnostic = f"{type(error).__name__}:{error}"
                    diagnostic_hash = sha256(diagnostic.encode()).hexdigest()
                    run.tool_executions.append(
                        ToolExecution(
                            task_id=task.id,
                            tool_name=task.tool_name,
                            status="FAILED",
                            result_hash=diagnostic_hash,
                            started_at=tool_started_at,
                            error_type=type(error).__name__,
                            error_message=str(error)[:1000],
                            error_hash=diagnostic_hash,
                        )
                    )
                    task.state = "FAILED"
                    return self._fail(
                        run,
                        f"evidence provider failed for task {task.id}: {type(error).__name__}: {error}",
                        lease_id,
                    )
                self._ensure_lease(heartbeat_lost)
                qualified = [self._qualify(record, task) for record in records]
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
                run.tool_executions.append(
                    ToolExecution(
                        task_id=task.id,
                        tool_name=task.tool_name,
                        status="SUCCEEDED",
                        result_hash=result_hash,
                        started_at=tool_started_at,
                    )
                )
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
            self._synthesize(run)
        except EvidenceProviderError as error:
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
        if run.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"}:
            return run
        run.completed_at = datetime.now(UTC)
        run.state = "CANCELLED"
        self._persist(run, "RUN_CANCELLED", {"reason": reason})
        return run

    def record_decision(self, run_id: str, decision: DecisionRecord) -> ResearchRun:
        run = self.get_run(run_id)
        if decision.target_id != (run.thesis.id if run.thesis else decision.target_id):
            raise ValueError("decision target does not belong to this run")
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
        if getattr(self.provider, "qualification_authority", "runtime") == "external":
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

    def _synthesize(self, run: ResearchRun) -> None:
        run.claims = []
        for task in run.tasks:
            observed = [record for record in run.evidence if record.task_id == task.id]
            qualified = [record for record in observed if record.qualification == "QUALIFIED"]
            stance_counts = ", ".join(
                f"{stance.lower()}={sum(record.stance == stance for record in observed)}"
                for stance in ("SUPPORTING", "COUNTER", "CONFLICTING")
            )
            statement = (
                f"{task.title}: {len(qualified)} of {len(observed)} observed evidence records qualified "
                f"({stance_counts})."
            )
            claim = Claim(
                task_id=task.id,
                statement=statement,
                evidence_ids=list(dict.fromkeys(item.id for item in qualified)),
                status="QUALIFIED" if self._task_is_qualified(run, task) else "NEEDS_REVIEW",
                confidence=round(len(qualified) / len(observed), 4) if observed else 0.0,
            )
            verify_claim = getattr(self.provider, "verify_claim", None)
            if claim.status == "QUALIFIED" and claim.evidence_ids and callable(verify_claim) and not verify_claim(claim.statement, claim.evidence_ids):
                claim.status = "NEEDS_REVIEW"
            run.claims.append(claim)
        claim_ids = [claim.id for claim in run.claims]
        qualified_count = sum(claim.status == "QUALIFIED" for claim in run.claims)
        qualified_supporting = self._task_titles_with_stance(run, "SUPPORTING")
        qualified_downside = self._task_titles_with_stance(run, "COUNTER") + self._task_titles_with_stance(run, "CONFLICTING")
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(run, task, requirement.id)
        ]
        bull_subjects = ", ".join(qualified_supporting) or "no task"
        downside_subjects = ", ".join(dict.fromkeys(qualified_downside)) or "no task"
        unresolved_text = ", ".join(unresolved) or "none"
        run.thesis = Thesis(
            statement=f"Observed evidence qualifies {qualified_count} of {len(run.tasks)} task claims; interpretation requires human review.",
            bull=f"Bull scenario: qualified supporting evidence is observed for {bull_subjects}; assumptions remain subject to review.",
            base=f"Base scenario: {qualified_count} of {len(run.tasks)} task claims are qualified, with unresolved requirements {unresolved_text}.",
            bear=f"Bear scenario: qualified counter or conflicting evidence is observed for {downside_subjects}; unresolved requirements are {unresolved_text}.",
            claim_ids=claim_ids,
            review_status="PENDING_REVIEW" if not unresolved else "NEEDS_REVIEW",
        )

    def _task_titles_with_stance(self, run: ResearchRun, stance: str) -> list[str]:
        return [
            task.title
            for task in run.tasks
            if any(
                record.task_id == task.id
                and record.stance == stance
                and record.qualification == "QUALIFIED"
                for record in run.evidence
            )
        ]

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
