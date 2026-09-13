from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchTask
from deepresearch.evaluation.scorer import score_run
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider


def test_evaluation_scores_only_observed_runtime_facts(tmp_path) -> None:
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    case = ResearchCase(id="case-1", question="Assess ACME's margin durability", target="ACME")
    task = ResearchTask(
        id="market",
        title="Market",
        purpose="Assess market",
        tool_name="deterministic-research",
        evidence_requirements=[EvidenceRequirement(id="req-market", description="one source")],
    )
    run = engine.execute(engine.create_run(case, [task]).id)
    result = score_run(run, {"case_id": "DR-001", "expected_state": "COMPLETED", "minimum_qualified_evidence": 1, "requires_claim": True})
    assert result.passed is True
    assert all(check.status == "PASS" for check in result.checks)
