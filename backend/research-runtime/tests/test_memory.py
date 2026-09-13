from deepresearch.domain.models import DecisionRecord, ResearchCase
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider


def test_investment_memory_retains_target_versions_and_decisions(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider())
    first_case = ResearchCase(id="case-1", question="Assess ACME margins", target="ACME")
    second_case = ResearchCase(id="case-2", question="Reassess ACME margins", target="ACME")

    first = engine.execute(engine.create_run(first_case).id)
    first_memory = engine.get_memory("ACME")
    assert first.thesis is not None
    assert first.memo is not None
    assert first_memory.run_ids == [first.id]
    assert first_memory.latest_run_id == first.id
    assert first_memory.previous_thesis_id is None

    decision = DecisionRecord(
        actor="analyst@example.com",
        action="REJECT_THESIS",
        target_id=first.thesis.id,
        rationale="Keep the thesis under review until counter-evidence is resolved.",
    )
    engine.record_decision(first.id, decision)
    second = engine.execute(engine.create_run(second_case).id)

    memory = engine.get_memory("ACME")
    assert memory.case_ids == [first_case.id, second_case.id]
    assert memory.run_ids == [first.id, second.id]
    assert memory.memo_ids == [first.memo.id, second.memo.id]
    assert memory.thesis_ids == [first.thesis.id, second.thesis.id]
    assert memory.latest_run_id == second.id
    assert memory.latest_thesis_id == second.thesis.id
    assert memory.previous_thesis_id == first.thesis.id
    assert memory.decision_ids == [decision.id]

    reloaded = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    assert reloaded.get_memory("ACME") == memory
