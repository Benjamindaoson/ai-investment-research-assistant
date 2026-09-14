from deepresearch.domain.models import (
    DecisionRecord,
    EvidenceRequirement,
    InvestmentCommitteeReview,
    RedTeamReview,
    ResearchCase,
    ResearchRun,
    ResearchTask,
)
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


def test_evaluation_rejects_run_with_missing_memo_sections(tmp_path) -> None:
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    case = ResearchCase(id="case-2", question="Assess ACME", target="ACME")
    task = ResearchTask(
        id="market",
        title="Market",
        purpose="Assess market",
        tool_name="deterministic-research",
        evidence_requirements=[EvidenceRequirement(id="req-market", description="one source")],
    )
    run = engine.execute(engine.create_run(case, [task]).id)
    assert run.memo is not None
    run.memo.sections = []

    result = score_run(run, {"case_id": "DR-002", "expected_state": "COMPLETED"})

    assert result.passed is False
    assert next(check for check in result.checks if check.name == "memo_sections").status == "FAIL"


def _completed_run(tmp_path):
    engine = ResearchEngine(SQLiteStore(tmp_path / "runtime.sqlite3"), DeterministicEvidenceProvider())
    case = ResearchCase(id="case-ic", question="Assess ACME", target="ACME")
    task = ResearchTask(
        id="market",
        title="Market",
        purpose="Assess market",
        tool_name="deterministic-research",
        evidence_requirements=[EvidenceRequirement(id="req-market", description="one source")],
    )
    return engine, engine.execute(engine.create_run(case, [task]).id)


def _ic_review(run: ResearchRun, evidence_id: str, *, thesis_id: str | None = None) -> InvestmentCommitteeReview:
    assert run.thesis is not None
    return InvestmentCommitteeReview(
        id="ic-financial",
        run_id=run.id,
        thesis_id=thesis_id or run.thesis.id,
        role="FINANCIAL",
        reviewer="CFO",
        position="MIXED",
        recommendation="HOLD",
        rationale="Validate margin durability before sizing the position.",
        evidence_ids=[evidence_id],
    )


def _red_team_review(run: ResearchRun, evidence_id: str, *, thesis_id: str | None = None) -> RedTeamReview:
    assert run.thesis is not None
    return RedTeamReview(
        id="red-team-review",
        run_id=run.id,
        thesis_id=thesis_id or run.thesis.id,
        reviewer="Independent analyst",
        challenge="The growth signal may not persist through the next cycle.",
        evidence_ids=[evidence_id],
        outcome="SUPPORTED",
        rationale="The counter-evidence is material to the downside case.",
    )


def test_evaluation_accepts_evidence_linked_ic_reviews_in_memo_and_decision(tmp_path) -> None:
    engine, run = _completed_run(tmp_path)
    assert run.thesis is not None
    assert run.evidence

    review = _ic_review(run, run.evidence[0].id)
    run = engine.record_ic_review(run.id, review)
    run = engine.record_decision(
        run.id,
        DecisionRecord(
            actor="IC chair",
            action="REQUEST_RESEARCH",
            target_id=run.thesis.id,
            rationale="Review evidence before final approval.",
            review_ids=[review.id],
        ),
    )

    result = score_run(
        run,
        {
            "case_id": "DR-IC-PASS",
            "expected_state": "COMPLETED",
            "required_ic_review_roles": ["FINANCIAL"],
        },
    )

    assert result.passed is True
    assert next(check for check in result.checks if check.name == "ic_review_links").status == "PASS"
    assert next(check for check in result.checks if check.name == "ic_review_coverage").status == "PASS"


def test_evaluation_rejects_dangling_ic_review_reference(tmp_path) -> None:
    _, run = _completed_run(tmp_path)
    assert run.memo is not None
    run.memo.ic_review_ids = ["missing-review"]

    result = score_run(run, {"case_id": "DR-IC-DANGLING", "expected_state": "COMPLETED"})

    assert result.passed is False
    check = next(check for check in result.checks if check.name == "ic_review_links")
    assert check.status == "FAIL"
    assert "missing-review" in check.detail


def test_evaluation_rejects_cross_thesis_ic_review_reference(tmp_path) -> None:
    _, run = _completed_run(tmp_path)
    assert run.thesis is not None
    assert run.memo is not None
    review = _ic_review(run, run.evidence[0].id, thesis_id="thesis-other")
    run.ic_reviews.append(review)
    run.memo.ic_review_ids = [review.id]

    result = score_run(run, {"case_id": "DR-IC-CROSS-THESIS", "expected_state": "COMPLETED"})

    assert result.passed is False
    check = next(check for check in result.checks if check.name == "ic_review_links")
    assert check.status == "FAIL"
    assert "ic-financial" in check.detail


def test_evaluation_rejects_missing_required_ic_review_role(tmp_path) -> None:
    engine, run = _completed_run(tmp_path)
    review = _ic_review(run, run.evidence[0].id)
    run = engine.record_ic_review(run.id, review)

    result = score_run(
        run,
        {
            "case_id": "DR-IC-COVERAGE",
            "expected_state": "COMPLETED",
            "required_ic_review_roles": ["FINANCIAL", "BEAR"],
        },
    )

    assert result.passed is False
    check = next(check for check in result.checks if check.name == "ic_review_coverage")
    assert check.status == "FAIL"
    assert "BEAR" in check.detail


def test_evaluation_accepts_evidence_linked_red_team_review(tmp_path) -> None:
    engine, run = _completed_run(tmp_path)
    counter_id = next(item.id for item in run.evidence if item.stance == "COUNTER")
    run = engine.record_red_team_review(run.id, _red_team_review(run, counter_id))

    result = score_run(
        run,
        {"case_id": "DR-RED-PASS", "expected_state": "COMPLETED", "minimum_red_team_reviews": 1},
    )

    assert result.passed is True
    assert next(check for check in result.checks if check.name == "red_team_links").status == "PASS"
    assert next(check for check in result.checks if check.name == "red_team_coverage").status == "PASS"


def test_evaluation_rejects_invalid_red_team_evidence_links(tmp_path) -> None:
    _, run = _completed_run(tmp_path)
    counter_id = next(item.id for item in run.evidence if item.stance == "COUNTER")
    supporting_id = next(item.id for item in run.evidence if item.stance == "SUPPORTING")
    review = _red_team_review(run, counter_id, thesis_id="thesis-other")
    review.evidence_ids = [supporting_id, "missing-evidence"]
    run.red_team_reviews.append(review)

    result = score_run(run, {"case_id": "DR-RED-INVALID", "expected_state": "COMPLETED"})

    assert result.passed is False
    check = next(check for check in result.checks if check.name == "red_team_links")
    assert check.status == "FAIL"
    assert "red-team-review" in check.detail
    assert "missing-evidence" in check.detail
    assert supporting_id in check.detail


def test_evaluation_rejects_insufficient_red_team_reviews(tmp_path) -> None:
    _, run = _completed_run(tmp_path)

    result = score_run(
        run,
        {"case_id": "DR-RED-COVERAGE", "expected_state": "COMPLETED", "minimum_red_team_reviews": 1},
    )

    assert result.passed is False
    check = next(check for check in result.checks if check.name == "red_team_coverage")
    assert check.status == "FAIL"
    assert "observed=0, minimum=1" in check.detail
