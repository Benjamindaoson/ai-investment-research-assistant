from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchTask,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider


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

    interrupted = engine.execute(run.id, stop_after_tasks=1)
    assert interrupted.state == "RUNNING"
    assert interrupted.tasks[0].state == "COMPLETED"
    assert interrupted.plan is not None
    assert interrupted.plan.status == "VALIDATED"
    assert interrupted.plan.tasks[0].state == "PENDING"
    assert len(interrupted.tool_executions) == 1

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
    assert result.memo.unresolved_requirement_ids == ["risk:req-risk"]
    assert {"risk:req-risk"} <= set(result.memo.sections[0].unresolved_requirement_ids)
    assert all(section.body for section in result.memo.sections)


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


def test_engine_records_provider_failure_without_successful_tool_execution(tmp_path) -> None:
    class FailingProvider(DeterministicEvidenceProvider):
        def collect(self, task, case):
            raise RuntimeError("provider unavailable")

    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), FailingProvider())
    case = ResearchCase(id="case-3", question="Assess ACME's margin durability", target="ACME")
    run = engine.create_run(case, [make_task("market")])

    result = engine.execute(run.id)

    assert result.state == "FAILED"
    assert result.tasks[0].state == "FAILED"
    assert result.tool_executions == []
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
