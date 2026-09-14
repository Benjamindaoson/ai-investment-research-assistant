from hashlib import sha256
from threading import Event, Thread

from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchPlan,
    ResearchRun,
    ResearchTask,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine, RunLeaseConflictError, RunLeaseLostError
from deepresearch.runtime.evidence import DeterministicEvidenceProvider, EvidenceProviderError
from deepresearch.runtime.planner import research_input_hash


def make_task(task_id: str, depends_on: list[str] | None = None) -> ResearchTask:
    return ResearchTask(
        id=task_id,
        title=task_id,
        purpose="Evaluate a financial research dimension",
        depends_on=depends_on or [],
        tool_name="deterministic-research",
        evidence_requirements=[EvidenceRequirement(id=f"req-{task_id}", description="one source")],
    )


def test_engine_executes_dag_and_resumes_without_duplicate_tools(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider)
    case = ResearchCase(id="case-1", question="Assess ACME's margin durability", target="ACME")
    run = engine.create_run(case, [make_task("market"), make_task("thesis", ["market"])])
    expected_input_hash = engine._task_input_hash(case, run.tasks[0])

    interrupted = engine.execute(run.id, stop_after_tasks=1)
    assert interrupted.state == "RUNNING"
    assert interrupted.tasks[0].state == "COMPLETED"
    assert interrupted.plan is not None
    assert interrupted.plan.status == "VALIDATED"
    assert interrupted.plan.tasks[0].state == "PENDING"
    assert len(interrupted.tool_executions) == 1
    assert interrupted.tool_executions[0].provider == "deterministic-demo"
    assert interrupted.tool_executions[0].input_hash == expected_input_hash
    assert interrupted.tool_executions[0].evidence_count == 2
    assert interrupted.tool_executions[0].qualified_evidence_count == 1
    assert interrupted.tool_executions[0].review_evidence_count == 1
    assert interrupted.tool_executions[0].unqualified_evidence_count == 0

    resumed = engine.execute(run.id)
    assert resumed.state == "COMPLETED"
    assert len(resumed.tool_executions) == 2
    assert len(provider.calls) == 2
    assert any(event["event_type"] == "RUN_RESUMED" for event in engine.store.events(run.id))
    assert resumed.thesis is not None
    assert all(claim.evidence_ids for claim in resumed.claims)
    assert all(claim.confidence == 0.5 for claim in resumed.claims)
    assert all("Operating momentum" not in claim.statement for claim in resumed.claims)
    assert "qualified" in resumed.thesis.base.lower()
    assert "operating momentum" not in resumed.thesis.bull.lower()
    assert resumed.memo is not None
    assert [section.section_key for section in resumed.memo.sections] == [
        "thesis", "evidence", "risks", "scenarios", "decision"
    ]
    assert set(resumed.memo.sections[0].claim_ids) == {claim.id for claim in resumed.claims}
    assert set(resumed.memo.sections[0].evidence_ids) <= {record.id for record in resumed.evidence}


def test_engine_keeps_same_case_runs_independent(tmp_path) -> None:
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    case = ResearchCase(id="case-repeat", question="Reassess ACME", target="ACME")

    first = engine.create_run(case, [make_task("market")])
    second = engine.create_run(case, [make_task("market")])
    first_result = engine.execute(first.id)
    second_result = engine.execute(second.id)

    assert first.id != second.id
    assert engine.get_run(first.id).case_id == case.id
    assert engine.get_run(second.id).case_id == case.id
    assert first_result.state == second_result.state == "COMPLETED"
    assert engine.get_memory("ACME").run_ids == [first.id, second.id]


def test_engine_marks_missing_evidence_partial(tmp_path) -> None:
    class EmptyProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            self.calls.append(task.id)
            return []

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), EmptyProvider())
    case = ResearchCase(id="case-2", question="Assess ACME's downside risk", target="ACME")
    run = engine.create_run(case, [make_task("risk")])
    result = engine.execute(run.id)
    assert result.state == "PARTIAL"
    assert result.thesis is not None
    assert result.thesis.review_status == "NEEDS_REVIEW"
    assert result.claims[0].status == "NEEDS_REVIEW"
    assert result.claims[0].evidence_ids == []
    assert result.claims[0].confidence == 0.0
    assert "unresolved" in result.thesis.bear.lower()
    assert result.memo is not None
    assert result.memo.status == "DRAFT"
    assert result.tool_executions[0].status == "SUCCEEDED"
    assert result.tool_executions[0].result_hash == sha256(b"empty").hexdigest()
    assert result.tool_executions[0].evidence_count == 0
    assert result.tool_executions[0].qualified_evidence_count == 0
    assert result.tool_executions[0].review_evidence_count == 0
    assert result.tool_executions[0].unqualified_evidence_count == 0
    assert result.memo.unresolved_requirement_ids == ["risk:req-risk"]
    assert {"risk:req-risk"} <= set(result.memo.sections[0].unresolved_requirement_ids)
    assert all(section.body for section in result.memo.sections)


def test_engine_persists_unknown_attempt_before_provider_call(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    observed = []

    class InspectingProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            persisted = ResearchRun.model_validate(store.get_run(run.id))
            observed.append(persisted.tool_executions[-1])
            return super().collect(task, case)

    provider = InspectingProvider()
    engine = ResearchEngine(store, provider)
    run = engine.create_run(
        ResearchCase(id="case-attempt", question="Assess ACME attempt durability", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)

    assert result.state == "COMPLETED"
    assert observed[0].status == "UNKNOWN_EFFECT"
    assert observed[0].completed_at is None
    assert observed[0].attempt_key.startswith(f"{run.id}:market:attempt-")
    assert result.tool_executions[0].status == "SUCCEEDED"
    assert result.tool_executions[0].attempt_key == observed[0].attempt_key
    assert result.tool_executions[0].completed_at is not None


def test_engine_requires_complete_provenance_before_qualifying_evidence(tmp_path) -> None:
    class IncompleteProvider:
        def collect(self, task, case):
            return [
                EvidenceRecord(
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    source_id="source-without-locator",
                    source_title="Unresolved source",
                    excerpt="The source identity is not sufficiently anchored.",
                    provider="test-provider",
                )
            ]

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), IncompleteProvider())
    run = engine.create_run(
        ResearchCase(id="case-provenance", question="Assess ACME evidence quality", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)

    assert result.state == "PARTIAL"
    assert result.evidence[0].qualification == "NEEDS_REVIEW"
    assert result.claims[0].evidence_ids == []
    assert result.memo is not None
    assert result.memo.unresolved_requirement_ids == ["market:req-market"]
    assert engine.trace(run.id)["evidence"] == {
        "total": 1,
        "by_qualification": {"QUALIFIED": 0, "NEEDS_REVIEW": 1, "UNQUALIFIED": 0},
        "provenance_complete": 0,
        "provenance_incomplete": 1,
    }


def test_engine_preserves_external_finevidence_qualification(tmp_path) -> None:
    class ExternalProvider:
        qualification_authority = "external"

        def collect(self, task, case):
            return [
                EvidenceRecord(
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    qualification="NEEDS_REVIEW",
                    source_id="finevidence-doc",
                    source_title="External document",
                    excerpt="FinEvidence marked the requirement partial.",
                    provider="finevidence-http",
                    source_url="https://example.test/document",
                    locator="page:1",
                    content_hash="b" * 64,
                    provenance={"finevidence": {"coverage_status": "PARTIAL"}},
                )
            ]

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), ExternalProvider())
    run = engine.create_run(
        ResearchCase(id="case-external", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)

    assert result.state == "PARTIAL"
    assert result.evidence[0].qualification == "NEEDS_REVIEW"


def test_engine_replans_partial_run_and_resumes_same_run(tmp_path) -> None:
    class EventuallyAvailable(DeterministicEvidenceProvider):
        attempt = 0

        def collect(self, task, case):
            self.attempt += 1
            if self.attempt == 1:
                self.calls.append(task.id)
                return []
            return super().collect(task, case)

    provider = EventuallyAvailable()
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider)
    run = engine.create_run(
        ResearchCase(id="case-replan", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )

    partial = engine.execute(run.id)
    replanned = engine.replan(run.id)
    completed = engine.execute(run.id)

    assert partial.state == "PARTIAL"
    assert replanned.id == run.id
    assert replanned.state == "CREATED"
    assert replanned.plan is not None
    assert replanned.plan.provenance["replan_unresolved_requirement_ids"] == ["market:req-market"]
    assert completed.state == "COMPLETED"
    assert completed.id == run.id
    assert len(completed.evidence) == 2
    assert [event["event_type"] for event in engine.store.events(run.id)].count("RUN_REPLANNED") == 1


def test_engine_replan_rejects_completed_run_without_mutation(tmp_path) -> None:
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    run = engine.create_run(
        ResearchCase(id="case-no-replan", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )
    completed = engine.execute(run.id)
    before = engine.store.events(run.id)

    try:
        engine.replan(run.id)
    except ValueError as error:
        assert str(error) == "only partial runs can be replanned"
    else:
        raise AssertionError("completed run was replanned")

    assert engine.get_run(run.id) == completed
    assert engine.store.events(run.id) == before


def test_engine_replan_adds_new_task_and_preserves_completed_work(tmp_path) -> None:
    class ExpandingPlanner:
        name = "expanding-test-planner"
        version = "v1"
        supports_dynamic_tasks = True

        def plan(self, case):
            return ResearchPlan(
                case_id=case.id,
                question=case.question,
                planner_name=self.name,
                planner_version=self.version,
                input_hash=research_input_hash(case),
                tasks=[make_task("market"), make_task("risk", ["market"]), make_task("new")],
            )

        def replan(self, case, unresolved_requirement_ids):
            return self.plan(case)

    class PartialProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            if task.id == "risk" and task.id not in self.calls:
                self.calls.append(task.id)
                return []
            return super().collect(task, case)

    provider = PartialProvider()
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider, planner=ExpandingPlanner())
    run = engine.create_run(
        ResearchCase(id="case-dynamic", question="Assess ACME evidence", target="ACME"),
        [make_task("market"), make_task("risk", ["market"])],
    )

    partial = engine.execute(run.id)
    replanned = engine.replan(run.id)
    completed = engine.execute(run.id)

    assert partial.state == "PARTIAL"
    assert replanned.id == run.id
    assert [task.id for task in replanned.tasks] == ["market", "risk", "new"]
    assert replanned.tasks[0].state == "COMPLETED"
    assert len(replanned.evidence) == 2
    assert completed.state == "COMPLETED"
    assert completed.tasks[-1].state == "COMPLETED"
    assert [event["event_type"] for event in engine.store.events(run.id)].count("RUN_REPLANNED") == 1


def test_engine_replan_rejects_unknown_dependency_without_mutation(tmp_path) -> None:
    class InvalidExpandingPlanner:
        name = "invalid-expanding-test-planner"
        version = "v1"
        supports_dynamic_tasks = True

        def plan(self, case):
            return ResearchPlan(
                case_id=case.id,
                question=case.question,
                planner_name=self.name,
                planner_version=self.version,
                input_hash=research_input_hash(case),
                tasks=[make_task("market"), make_task("new", ["missing"])],
            )

        def replan(self, case, unresolved_requirement_ids):
            return self.plan(case)

    class EmptyProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            self.calls.append(task.id)
            return []

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), EmptyProvider(), planner=InvalidExpandingPlanner())
    run = engine.create_run(
        ResearchCase(id="case-invalid-dynamic", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )
    partial = engine.execute(run.id)
    before = engine.store.events(run.id)

    try:
        engine.replan(run.id)
    except ValueError as error:
        assert "unknown tasks" in str(error)
    else:
        raise AssertionError("invalid dynamic plan was accepted")

    assert engine.get_run(run.id) == partial
    assert engine.store.events(run.id) == before


def test_engine_requires_external_claim_verification_for_completion(tmp_path) -> None:
    class UnsupportedClaimProvider:
        qualification_authority = "external"

        def collect(self, task, case):
            return [
                EvidenceRecord(
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    qualification="QUALIFIED",
                    source_id="source",
                    source_title="Source",
                    excerpt="Observed evidence",
                    provider="finevidence-http",
                    source_url="https://example.test/source",
                    locator="page:1",
                    content_hash="d" * 64,
                    provenance={"finevidence": {"coverage_status": "ELIGIBLE"}},
                )
            ]

        def verify_claim(self, claim, evidence_ids):
            return False

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), UnsupportedClaimProvider())
    run = engine.create_run(
        ResearchCase(id="case-claim-review", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)

    assert result.state == "PARTIAL"
    assert result.claims[0].status == "NEEDS_REVIEW"
    assert result.completed_at is not None


def test_engine_records_claim_verification_transport_failure(tmp_path) -> None:
    class FailingVerifier:
        qualification_authority = "external"

        def collect(self, task, case):
            return [
                EvidenceRecord(
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    qualification="QUALIFIED",
                    source_id="source",
                    source_title="Source",
                    excerpt="Observed evidence",
                    provider="finevidence-http",
                    source_url="https://example.test/source",
                    locator="page:1",
                    content_hash="e" * 64,
                    provenance={"finevidence": {"coverage_status": "ELIGIBLE"}},
                )
            ]

        def verify_claim(self, claim, evidence_ids):
            raise EvidenceProviderError("verification unavailable")

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), FailingVerifier())
    run = engine.create_run(
        ResearchCase(id="case-claim-failure", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)

    assert result.state == "FAILED"
    assert any(
        event["event_type"] == "RUN_FAILED" and "verification unavailable" in event["payload"]["reason"]
        for event in engine.store.events(run.id)
    )


def test_engine_retries_replace_same_evidence_when_qualification_changes(tmp_path) -> None:
    class QualificationProvider:
        qualification_authority = "external"
        attempt = 0

        def collect(self, task, case):
            self.attempt += 1
            return [
                EvidenceRecord(
                    id="stable-evidence",
                    task_id=task.id,
                    requirement_id=task.evidence_requirements[0].id,
                    stance="SUPPORTING",
                    qualification="NEEDS_REVIEW" if self.attempt == 1 else "QUALIFIED",
                    source_id="source",
                    source_title="Source",
                    excerpt="Observed evidence",
                    provider="finevidence-http",
                    source_url="https://example.test/source",
                    locator="page:1",
                    content_hash="c" * 64,
                    provenance={"finevidence": {"coverage_status": "PARTIAL"}},
                )
            ]

    provider = QualificationProvider()
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider)
    run = engine.create_run(
        ResearchCase(id="case-evidence-retry", question="Assess ACME evidence", target="ACME"),
        [make_task("market")],
    )

    engine.execute(run.id)
    engine.replan(run.id)
    completed = engine.execute(run.id)

    assert completed.state == "COMPLETED"
    assert len(completed.evidence) == 1
    assert completed.evidence[0].qualification == "QUALIFIED"


def test_engine_records_provider_failure_as_failed_tool_execution(tmp_path) -> None:
    message = "provider unavailable: " + "x" * 1200

    class FailingProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            raise RuntimeError(message)

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), FailingProvider())
    case = ResearchCase(id="case-3", question="Assess ACME's margin durability", target="ACME")
    run = engine.create_run(case, [make_task("market")])

    result = engine.execute(run.id)

    assert result.state == "FAILED"
    assert result.tasks[0].state == "FAILED"
    assert len(result.tool_executions) == 1
    failure = result.tool_executions[0]
    assert failure.status == "FAILED"
    assert failure.error_type == "RuntimeError"
    assert failure.error_message == message[:1000]
    assert failure.error_hash == sha256(f"RuntimeError:{message}".encode()).hexdigest()
    assert failure.result_hash == failure.error_hash
    assert failure.provider == "deterministic-demo"
    assert len(failure.input_hash or "") == 64
    assert failure.evidence_count == 0
    assert len(failure.error_hash) == 64
    assert any(event["event_type"] == "RUN_FAILED" for event in engine.store.events(run.id))


def test_engine_cancellation_is_terminal_idempotent_and_not_resumable(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), provider)
    case = ResearchCase(id="case-4", question="Assess ACME's downside risk", target="ACME")
    run = engine.create_run(case, [make_task("risk")])

    cancelled = engine.cancel(run.id, "Analyst stopped the run")
    repeated = engine.cancel(run.id, "Repeated request")
    executed = engine.execute(run.id)

    assert cancelled.state == "CANCELLED"
    assert cancelled.completed_at is not None
    assert cancelled.thesis is None
    assert repeated == cancelled
    assert executed.state == "CANCELLED"
    assert provider.calls == []
    assert [event["event_type"] for event in engine.store.events(run.id)].count("RUN_CANCELLED") == 1


def test_engine_rejects_active_lease_without_provider_work(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, provider)
    run = engine.create_run(
        ResearchCase(id="case-lease-conflict", question="Assess ACME lease safety", target="ACME"),
        [make_task("market")],
    )
    assert store.acquire_run_lease(run.id, "other-executor", 60)

    try:
        engine.execute(run.id)
    except RunLeaseConflictError as error:
        assert str(error) == f"research run {run.id} is already being executed"
    else:
        raise AssertionError("active lease was ignored")

    assert provider.calls == []
    assert engine.get_run(run.id).state == "CREATED"


def test_engine_records_lease_lifecycle_and_releases_on_failure(tmp_path) -> None:
    class FailingProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            raise RuntimeError("provider unavailable")

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, FailingProvider())
    run = engine.create_run(
        ResearchCase(id="case-lease-failure", question="Assess ACME lease failure", target="ACME"),
        [make_task("market")],
    )

    result = engine.execute(run.id)
    events = store.events(run.id)
    acquired = next(event for event in events if event["event_type"] == "RUN_LEASE_ACQUIRED")
    released = next(event for event in events if event["event_type"] == "RUN_LEASE_RELEASED")

    assert result.state == "FAILED"
    assert acquired["payload"]["lease_id"] == released["payload"]["lease_id"]
    assert released["payload"]["released"] is True
    assert store.acquire_run_lease(run.id, "later-executor", 60)


def test_terminal_execution_is_idempotent_without_lease_events(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, provider)
    run = engine.create_run(
        ResearchCase(id="case-lease-terminal", question="Assess ACME terminal run", target="ACME"),
        [make_task("market")],
    )

    completed = engine.execute(run.id)
    repeated = engine.execute(run.id)

    assert completed.state == repeated.state == "COMPLETED"
    assert len(provider.calls) == 1
    assert [event["event_type"] for event in store.events(run.id)].count("RUN_LEASE_ACQUIRED") == 1


def test_stop_after_tasks_releases_lease_for_resume(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider())
    run = engine.create_run(
        ResearchCase(id="case-lease-resume", question="Assess ACME resume", target="ACME"),
        [make_task("market"), make_task("risk", ["market"])],
    )

    partial = engine.execute(run.id, stop_after_tasks=1)
    resumed = engine.execute(run.id)
    events = store.events(run.id)

    assert partial.state == "RUNNING"
    assert resumed.state == "COMPLETED"
    assert len([event for event in events if event["event_type"] == "RUN_LEASE_ACQUIRED"]) == 2
    assert len([event for event in events if event["event_type"] == "RUN_LEASE_RELEASED"]) == 2


def test_engine_heartbeat_keeps_ownership_during_slow_provider(tmp_path) -> None:
    started = Event()
    release = Event()
    renewed = Event()

    class SlowProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            started.set()
            assert release.wait(2)
            return super().collect(task, case)

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    original_renew = store.renew_run_lease

    def track_renewal(run_id, lease_id, ttl_seconds):
        result = original_renew(run_id, lease_id, ttl_seconds)
        renewed.set()
        return result

    store.renew_run_lease = track_renewal
    engine = ResearchEngine(store, SlowProvider(), lease_seconds=1.0)
    run = engine.create_run(
        ResearchCase(id="case-heartbeat", question="Assess ACME heartbeat", target="ACME"),
        [make_task("market")],
    )
    result_holder = []
    execution = Thread(target=lambda: result_holder.append(engine.execute(run.id)))
    execution.start()
    assert started.wait(1)
    assert renewed.wait(1)
    assert store.acquire_run_lease(run.id, "other-executor", 1) is False
    release.set()
    execution.join(2)

    assert not execution.is_alive()
    assert result_holder[0].state == "COMPLETED"


def test_engine_discards_result_after_lease_loss_and_allows_takeover(monkeypatch, tmp_path) -> None:
    started = Event()
    release = Event()
    lost = Event()

    class BlockingProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            started.set()
            assert release.wait(2)
            return super().collect(task, case)

    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    original_renew = store.renew_run_lease

    def lose_renewal(run_id, lease_id, ttl_seconds):
        lost.set()
        return False

    monkeypatch.setattr(store, "renew_run_lease", lose_renewal)
    provider = BlockingProvider()
    engine = ResearchEngine(store, provider, lease_seconds=0.3)
    run = engine.create_run(
        ResearchCase(id="case-lease-loss", question="Assess ACME lease loss", target="ACME"),
        [make_task("market")],
    )
    errors = []
    execution = Thread(target=lambda: _capture_error(errors, lambda: engine.execute(run.id)))
    execution.start()
    assert started.wait(1)
    assert lost.wait(1)
    release.set()
    execution.join(2)
    monkeypatch.setattr(store, "renew_run_lease", original_renew)

    assert not execution.is_alive()
    assert isinstance(errors[0], RunLeaseLostError)
    assert engine.get_run(run.id).tasks[0].state == "RUNNING"

    recovered = engine.execute(run.id)

    assert recovered.state == "BLOCKED"
    assert recovered.completed_at is None
    assert recovered.tasks[0].state == "UNKNOWN_EFFECT"
    assert len(recovered.tool_executions) == 1
    assert recovered.tool_executions[0].status == "UNKNOWN_EFFECT"
    assert provider.calls == ["market"]
    assert any(event["event_type"] == "TOOL_ATTEMPT_UNKNOWN_EFFECT" for event in store.events(run.id))

    retry = engine.resolve_tool_attempt(run.id, recovered.tool_executions[0].id, "RETRY")
    completed = engine.execute(retry.id)

    assert completed.state == "COMPLETED"
    assert len(completed.tool_executions) == 2
    assert completed.tool_executions[0].attempt_key != completed.tool_executions[1].attempt_key


def test_engine_blocks_legacy_running_task_without_attempt_and_can_mark_failed(tmp_path) -> None:
    provider = DeterministicEvidenceProvider()
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, provider)
    run = engine.create_run(
        ResearchCase(id="case-legacy-attempt", question="Assess ACME legacy recovery", target="ACME"),
        [make_task("market")],
    )
    payload = store.get_run(run.id)
    payload["state"] = "RUNNING"
    payload["tasks"][0]["state"] = "RUNNING"
    store.save_run(payload)

    blocked = engine.execute(run.id)
    attempt = blocked.tool_executions[0]
    failed = engine.resolve_tool_attempt(run.id, attempt.id, "MARK_FAILED")

    assert blocked.state == "BLOCKED"
    assert blocked.completed_at is None
    assert attempt.error_type == "LegacyRecovery"
    assert provider.calls == []
    assert failed.state == "FAILED"
    assert failed.tasks[0].state == "FAILED"
    assert any(event["event_type"] == "TOOL_ATTEMPT_MARKED_FAILED" for event in store.events(run.id))


def test_engine_loads_legacy_tool_receipt_with_execution_defaults(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider())
    run = engine.create_run(
        ResearchCase(id="case-legacy-receipt", question="Assess ACME legacy receipt", target="ACME"),
        [make_task("market")],
    )
    payload = store.get_run(run.id)
    payload["tool_executions"] = [{
        "id": "tool-legacy",
        "task_id": "market",
        "tool_name": "research",
        "status": "SUCCEEDED",
        "result_hash": "a" * 64,
    }]
    loaded = ResearchRun.model_validate(payload)

    assert loaded.tool_executions[0].provider == "unknown"
    assert loaded.tool_executions[0].input_hash is None
    assert loaded.tool_executions[0].evidence_count == 0
    assert loaded.tool_executions[0].unqualified_evidence_count == 0


def _capture_error(errors, operation) -> None:
    try:
        operation()
    except Exception as error:
        errors.append(error)
