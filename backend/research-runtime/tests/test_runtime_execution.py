from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
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
