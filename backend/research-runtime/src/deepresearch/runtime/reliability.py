"""Runtime reliability patches kept separate from the core engine implementation.

The helpers in this module are intentionally small monkey patches around
``ResearchEngine``.  Keeping them here lets the runtime harden recovery behavior
without duplicating the long execution loop.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from deepresearch.runtime.engine import RunLeaseLostError

_PENDING_COMPLETION_MEMORY = "_pending_completion_memory"


def _pending_claim_verification(run: Any) -> Any | None:
    return next(
        (
            execution
            for execution in reversed(run.tool_executions)
            if execution.operation == "CLAIM_VERIFICATION"
            and execution.status == "UNKNOWN_EFFECT"
            and execution.completed_at is None
        ),
        None,
    )


def _latest_task_input_hash(run: Any, task_id: str) -> str | None:
    return next(
        (
            execution.input_hash
            for execution in reversed(run.tool_executions)
            if execution.task_id == task_id
            and execution.operation == "EVIDENCE_COLLECTION"
            and execution.input_hash
        ),
        None,
    )


def patch_research_engine(engine_cls: type[Any]) -> None:
    """Install deterministic reliability fixes on ``ResearchEngine`` once."""

    if getattr(engine_cls, "_reliability_patch_applied", False):
        return

    original_execute = engine_cls._execute
    original_persist = engine_cls._persist
    original_build_memo = engine_cls._build_memo
    original_resolve_tool_attempt = engine_cls.resolve_tool_attempt

    def _execute(
        self: Any,
        run_id: str,
        stop_after_tasks: int | None = None,
        lease_id: str | None = None,
        heartbeat_lost: Any | None = None,
    ) -> Any:
        self._ensure_lease(heartbeat_lost)
        run = self.get_run(run_id)
        if run.state == "VERIFYING":
            receipt = _pending_claim_verification(run)
            if receipt is not None:
                run.state = "BLOCKED"
                run.completed_at = None
                self._persist(
                    run,
                    "CLAIM_VERIFICATION_UNKNOWN_EFFECT",
                    {
                        "claim_id": receipt.claim_id,
                        "task_id": receipt.task_id,
                        "attempt_id": receipt.id,
                        "attempt_key": receipt.attempt_key,
                    },
                    lease_id,
                )
                return run
        return original_execute(self, run_id, stop_after_tasks, lease_id, heartbeat_lost)

    def _build_memo(self: Any, run: Any, target: str) -> Any:
        memory = original_build_memo(self, run, target)
        setattr(self, _PENDING_COMPLETION_MEMORY, memory)
        return memory

    def _persist(
        self: Any,
        run: Any,
        event_type: str,
        payload: dict[str, object],
        lease_id: str | None = None,
    ) -> None:
        memory = getattr(self, _PENDING_COMPLETION_MEMORY, None)
        if event_type in {"RUN_COMPLETED", "RUN_PARTIAL"} and memory is not None:
            run.updated_at = datetime.now(UTC)
            run_payload = run.model_dump(mode="json")
            memory_payload = memory.model_dump(mode="json")
            if lease_id:
                save_owned = getattr(self.store, "save_run_event_memory_owned", None)
                if not callable(save_owned) or not save_owned(
                    run_payload,
                    lease_id,
                    event_type,
                    payload,
                    memory_payload,
                ):
                    raise RunLeaseLostError(f"research run {run.id} lease ownership was lost")
            else:
                save_atomic = getattr(self.store, "save_run_event_memory", None)
                if callable(save_atomic):
                    save_atomic(run_payload, event_type, payload, memory_payload)
                else:
                    original_persist(self, run, event_type, payload, lease_id)
                    self.store.save_memory(memory_payload)
            delattr(self, _PENDING_COMPLETION_MEMORY)
            return
        original_persist(self, run, event_type, payload, lease_id)

    def replan(self: Any, run_id: str) -> Any:
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
        replan_fn = getattr(self.planner, "replan", None)
        plan = replan_fn(case, unresolved) if callable(replan_fn) else self.planner.plan(case)
        if not plan.tasks:
            raise ValueError("replanner returned no tasks")
        existing_task_ids = {task.id for task in run.tasks}
        if not getattr(self.planner, "supports_dynamic_tasks", False):
            plan = plan.model_copy(update={"tasks": [task for task in plan.tasks if task.id in existing_task_ids]})
            if not plan.tasks:
                raise ValueError("replanner did not retain an existing task")

        planned = {task.id: task for task in plan.tasks}
        changed_task_ids: set[str] = set()
        for task in run.tasks:
            refreshed = planned.get(task.id)
            if refreshed is None:
                continue
            refreshed_input_hash = self._task_input_hash(case, refreshed)
            if self._task_input_hash(case, task) != refreshed_input_hash:
                changed_task_ids.add(task.id)
                continue
            previous_input_hash = _latest_task_input_hash(run, task.id)
            if task.state == "COMPLETED" and previous_input_hash and previous_input_hash != refreshed_input_hash:
                changed_task_ids.add(task.id)
        reset_task_ids = {item.split(":", 1)[0] for item in unresolved} | changed_task_ids
        merged_tasks = []
        for task in run.tasks:
            refreshed = planned.get(task.id, task)
            merged_tasks.append(refreshed.model_copy(update={"state": task.state}))
        for task in plan.tasks:
            if task.id not in existing_task_ids:
                reset_task_ids.add(task.id)
                merged_tasks.append(task.model_copy(update={"state": "PENDING"}))

        changed = True
        while changed:
            changed = False
            for task in merged_tasks:
                if task.id not in reset_task_ids and reset_task_ids.intersection(task.depends_on):
                    reset_task_ids.add(task.id)
                    changed = True
        merged_tasks = [
            task.model_copy(update={"state": "PENDING"}) if task.id in reset_task_ids else task
            for task in merged_tasks
        ]
        merged_plan = plan.model_copy(update={"tasks": merged_tasks})
        self._validate_plan(merged_plan, case)

        removed_evidence_count = sum(record.task_id in reset_task_ids for record in run.evidence)
        removed_tool_execution_count = sum(execution.task_id in reset_task_ids for execution in run.tool_executions)
        run.evidence = [record for record in run.evidence if record.task_id not in reset_task_ids]
        run.tool_executions = [
            execution for execution in run.tool_executions if execution.task_id not in reset_task_ids
        ]
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
                "changed_task_ids": sorted(changed_task_ids),
                "reset_task_ids": sorted(reset_task_ids),
                "removed_evidence_count": removed_evidence_count,
                "removed_tool_execution_count": removed_tool_execution_count,
                "plan_id": plan.id,
            },
        )
        return run

    def resolve_tool_attempt(self: Any, run_id: str, attempt_id: str, action: str) -> Any:
        run = self.get_run(run_id)
        if run.state != "BLOCKED":
            raise ValueError("only blocked runs can resolve a tool attempt")
        attempt = next((item for item in run.tool_executions if item.id == attempt_id), None)
        if attempt is None or attempt.status != "UNKNOWN_EFFECT" or attempt.completed_at is not None:
            raise ValueError("unknown in-flight tool attempt not found")
        if attempt.operation != "CLAIM_VERIFICATION":
            return original_resolve_tool_attempt(self, run_id, attempt_id, action)
        if action == "RETRY":
            run.state = "CREATED"
            run.completed_at = None
            run.claims = []
            run.thesis = None
            run.memo = None
            event_type = "CLAIM_VERIFICATION_RETRY_AUTHORIZED"
            attempt.resolution = "RETRY_AUTHORIZED"
        elif action == "MARK_FAILED":
            run.completed_at = datetime.now(UTC)
            run.state = "FAILED"
            event_type = "CLAIM_VERIFICATION_MARKED_FAILED"
            attempt.resolution = "MARKED_FAILED"
        else:
            raise ValueError("action must be RETRY or MARK_FAILED")
        attempt.completed_at = datetime.now(UTC)
        attempt.error_type = "Resolved"
        attempt.error_message = f"Operator resolution: {action}"
        self._persist(run, event_type, {"attempt_id": attempt.id, "action": action})
        return run

    engine_cls._execute = _execute
    engine_cls._build_memo = _build_memo
    engine_cls._persist = _persist
    engine_cls.replan = replan
    engine_cls.resolve_tool_attempt = resolve_tool_attempt
    engine_cls._reliability_patch_applied = True
