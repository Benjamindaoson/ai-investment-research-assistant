from datetime import UTC, datetime
from hashlib import sha256

from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchPlan,
    ResearchTask,
    ToolExecution,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.planner import research_input_hash


def _task(purpose: str = "Assess fundamentals") -> ResearchTask:
    return ResearchTask(
        id="fundamentals",
        title="Financial fundamentals",
        purpose=purpose,
        tool_name="deterministic-research",
        evidence_requirements=[
            EvidenceRequirement(
                id="fundamental-signal",
                description="financial fundamentals and durability evidence",
            )
        ],
    )


class SameTaskPlanner:
    name = "same-task-planner"
    version = "v1"
    supports_dynamic_tasks = False

    def plan(self, case: ResearchCase) -> ResearchPlan:
        return self._plan(case, [])

    def replan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        return self._plan(case, unresolved_requirement_ids)

    def _plan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        return ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name=self.name,
            planner_version=self.version,
            input_hash=research_input_hash(case),
            tasks=[_task()],
            mandate=case.mandate,
            provenance={"unresolved": unresolved_requirement_ids},
        )


def _qualified_record(task: ResearchTask) -> EvidenceRecord:
    return EvidenceRecord(
        id="evidence-fundamentals",
        task_id=task.id,
        requirement_id=task.evidence_requirements[0].id,
        stance="SUPPORTING",
        qualification="QUALIFIED",
        source_id="source-1",
        source_title="ACME filing",
        excerpt="ACME reported durable revenue and margins.",
        provider="test-provider",
        source_url="https://example.invalid/acme",
        source_version="fixture-v1",
        locator="page:1",
        content_hash=sha256(b"evidence-fundamentals").hexdigest(),
    )


def test_replan_invalidates_completed_task_when_prior_input_hash_drifted(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider(), planner=SameTaskPlanner())
    case = ResearchCase(id="case-1", question="Assess ACME durability", target="ACME")
    old_task = _task()
    run = engine.create_run(case, tasks=[old_task])
    run.tasks[0].state = "COMPLETED"
    run.completed_at = datetime.now(UTC)
    run.state = "PARTIAL"
    run.evidence = [_qualified_record(old_task)]
    run.tool_executions = [
        ToolExecution(
            task_id=old_task.id,
            tool_name=old_task.tool_name,
            input_hash="0" * 64,
            status="SUCCEEDED",
            result_hash="1" * 64,
        )
    ]
    store.save_run(run.model_dump(mode="json"))

    replanned = engine.replan(run.id)

    assert replanned.state == "CREATED"
    assert replanned.completed_at is None
    assert replanned.tasks[0].state == "PENDING"
    assert replanned.evidence == []
    assert replanned.tool_executions == []
    event = store.events(run.id)[-1]
    assert event["event_type"] == "RUN_REPLANNED"
    assert event["payload"]["changed_task_ids"] == ["fundamentals"]
    assert event["payload"]["reset_task_ids"] == ["fundamentals"]
    assert event["payload"]["removed_evidence_count"] == 1
    assert event["payload"]["removed_tool_execution_count"] == 1


def test_verifying_run_blocks_on_unknown_claim_verification_receipt(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider(), planner=SameTaskPlanner())
    case = ResearchCase(id="case-verify", question="Assess ACME claim support", target="ACME")
    run = engine.create_run(case, tasks=[_task()])
    run.tasks[0].state = "COMPLETED"
    run.state = "VERIFYING"
    attempt = ToolExecution(
        task_id=run.tasks[0].id,
        claim_id="claim-1",
        tool_name="claim-verification",
        operation="CLAIM_VERIFICATION",
        status="UNKNOWN_EFFECT",
        attempt_key="claim-verification-attempt",
        result_hash="2" * 64,
        completed_at=None,
        error_type="InFlight",
        error_message="Claim verification result has not been acknowledged.",
        error_hash="3" * 64,
    )
    run.tool_executions.append(attempt)
    store.save_run(run.model_dump(mode="json"))

    blocked = engine.execute(run.id)

    assert blocked.state == "BLOCKED"
    events = store.events(run.id)
    assert any(event["event_type"] == "CLAIM_VERIFICATION_UNKNOWN_EFFECT" for event in events)

    resumed = engine.resolve_tool_attempt(run.id, attempt.id, "RETRY")

    assert resumed.state == "CREATED"
    assert resumed.claims == []
    assert resumed.thesis is None
    assert resumed.memo is None
    assert resumed.tool_executions[0].resolution == "RETRY_AUTHORIZED"
    assert resumed.tool_executions[0].completed_at is not None


def test_store_atomically_persists_run_completion_event_and_memory(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    run_payload = {"id": "run-atomic", "case_id": "case-atomic", "state": "COMPLETED"}
    memory_payload = {
        "target": "ACME",
        "latest_run_id": "run-atomic",
        "updated_at": "2026-10-08T00:00:00+00:00",
    }

    store.save_run_event_memory(run_payload, "RUN_COMPLETED", {"claim_count": 1}, memory_payload)

    assert store.get_run("run-atomic") == run_payload
    assert store.events("run-atomic")[-1]["event_type"] == "RUN_COMPLETED"
    assert store.get_memory("ACME") == memory_payload


def test_owned_atomic_completion_requires_current_lease(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    original = {"id": "run-owned", "case_id": "case-owned", "state": "CREATED"}
    completed = {"id": "run-owned", "case_id": "case-owned", "state": "COMPLETED"}
    memory_payload = {
        "target": "ACME",
        "latest_run_id": "run-owned",
        "updated_at": "2026-10-08T00:00:00+00:00",
    }
    store.save_run(original)

    assert not store.save_run_event_memory_owned(
        completed,
        "wrong-lease",
        "RUN_COMPLETED",
        {"claim_count": 1},
        memory_payload,
    )
    assert store.get_run("run-owned") == original
    assert store.events("run-owned") == []
    assert store.get_memory("ACME") is None

    assert store.acquire_run_lease("run-owned", "lease-1", 60)
    assert store.save_run_event_memory_owned(
        completed,
        "lease-1",
        "RUN_COMPLETED",
        {"claim_count": 1},
        memory_payload,
    )
    assert store.get_run("run-owned") == completed
    assert store.events("run-owned")[-1]["event_type"] == "RUN_COMPLETED"
    assert store.get_memory("ACME") == memory_payload
