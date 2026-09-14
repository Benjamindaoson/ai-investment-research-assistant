"""Single-machine MVP orchestration for the complete research artifact chain."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from deepresearch.domain.models import (
    DecisionRecord,
    EvaluationResult,
    FinancialFactSet,
    InvestmentCommitteeReview,
    RedTeamReview,
    ScenarioValuationInput,
)
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.financial import (
    FinancialAnalysisTool,
    ScenarioValuationTool,
    financial_snapshot_from_facts,
)

MVP_IC_ROLES = ("BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER")


class MvpWorkflowIncompleteError(ValueError):
    """Research execution did not reach the state required for synthesis."""

    def __init__(self, state: str) -> None:
        self.state = state
        super().__init__(f"MVP workflow requires COMPLETED research execution; observed {state}")


class MvpRedTeamInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: str = Field(min_length=1, max_length=200)
    challenge: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(min_length=1, max_length=100)
    outcome: Literal["OPEN", "SUPPORTED", "REJECTED", "REQUIRES_RESEARCH"] = "OPEN"
    rationale: str = Field(min_length=3, max_length=4000)


class MvpIcReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER"]
    reviewer: str = Field(min_length=1, max_length=200)
    position: Literal["SUPPORTIVE", "CHALLENGING", "MIXED", "INSUFFICIENT"]
    recommendation: Literal["APPROVE", "HOLD", "REJECT", "REQUEST_RESEARCH"]
    rationale: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(min_length=1, max_length=100)


class MvpDecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = Field(min_length=1, max_length=200)
    action: Literal["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]
    target_id: str = Field(min_length=1, max_length=120)
    rationale: str = Field(min_length=3, max_length=4000)


class MvpWorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    financial_facts: FinancialFactSet
    valuation: ScenarioValuationInput
    red_team: MvpRedTeamInput
    ic_reviews: list[MvpIcReviewInput] = Field(min_length=5, max_length=5)
    decision: MvpDecisionInput

    @model_validator(mode="after")
    def require_one_review_per_role(self) -> MvpWorkflowRequest:
        roles = [review.role for review in self.ic_reviews]
        if set(roles) != set(MVP_IC_ROLES):
            raise ValueError(f"MVP IC reviews must contain exactly {list(MVP_IC_ROLES)}")
        return self


class MvpWorkflowReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    run_id: str
    state: Literal["COMPLETED"]
    memo_status: str
    financial_analysis_input_hash: str
    valuation_scenarios_id: str
    red_team_review_id: str
    ic_review_ids: list[str]
    decision_id: str
    evaluation: EvaluationResult


def _require_qualified_evidence(engine: ResearchEngine, run_id: str, evidence_ids: list[str], label: str) -> None:
    run = engine.get_run(run_id)
    records = {record.id: record for record in run.evidence}
    missing = sorted(set(evidence_ids) - records.keys())
    if missing:
        raise ValueError(f"{label} evidence not found in run: {missing}")
    unqualified = sorted(
        evidence_id for evidence_id in set(evidence_ids) if records[evidence_id].qualification != "QUALIFIED"
    )
    if unqualified:
        raise ValueError(f"{label} evidence is not qualified: {unqualified}")


def complete_mvp_workflow(
    engine: ResearchEngine,
    financial_analysis: FinancialAnalysisTool,
    valuation_scenarios: ScenarioValuationTool,
    run_id: str,
    request: MvpWorkflowRequest,
) -> MvpWorkflowReceipt:
    """Run the complete local workflow while reusing all existing write paths."""

    run = engine.get_run(run_id)
    if run.state in {"CREATED", "PARTIAL"}:
        run = engine.execute(run_id)
    if run.state != "COMPLETED":
        raise MvpWorkflowIncompleteError(run.state)
    if run.thesis is None or run.memo is None:
        raise ValueError("completed research run is missing thesis or memo")

    snapshot, evidence_ids = financial_snapshot_from_facts(request.financial_facts)
    calculated_analysis = financial_analysis.analyze(snapshot, evidence_ids).model_copy(
        update={"financial_facts": request.financial_facts.facts}
    )
    if run.financial_analysis is None:
        engine.record_financial_analysis(run_id, calculated_analysis)
    elif run.financial_analysis.input_hash != calculated_analysis.input_hash or run.financial_analysis.financial_facts != calculated_analysis.financial_facts:
        raise ValueError("run already contains a different financial analysis")
    analysis = engine.get_financial_analysis(run_id)

    calculated_valuation = valuation_scenarios.analyze(run_id, run.case_id, request.valuation)
    if run.valuation_scenarios is None:
        engine.record_valuation_scenarios(run_id, calculated_valuation)
    elif run.valuation_scenarios.input_hash != calculated_valuation.input_hash:
        raise ValueError("run already contains different valuation scenarios")
    valuation = engine.get_valuation_scenarios(run_id)

    _require_qualified_evidence(engine, run_id, request.red_team.evidence_ids, "red-team")
    red_team = RedTeamReview(
        id=f"mvp-red-team-{run_id}",
        run_id=run_id,
        thesis_id=run.thesis.id,
        **request.red_team.model_dump(),
    )
    existing_red_team = next((item for item in run.red_team_reviews if item.id == red_team.id), None)
    if existing_red_team is None:
        engine.record_red_team_review(run_id, red_team)
    else:
        red_team = existing_red_team

    ic_review_ids: list[str] = []
    for item in request.ic_reviews:
        _require_qualified_evidence(engine, run_id, item.evidence_ids, f"IC {item.role}")
        review = InvestmentCommitteeReview(
            id=f"mvp-ic-{run_id}-{item.role.lower()}",
            run_id=run_id,
            thesis_id=run.thesis.id,
            **item.model_dump(),
        )
        existing_review = next((current for current in run.ic_reviews if current.id == review.id), None)
        if existing_review is None:
            engine.record_ic_review(run_id, review)
        else:
            review = existing_review
        ic_review_ids.append(review.id)

    decision = DecisionRecord(
        id=f"mvp-decision-{run_id}",
        review_ids=ic_review_ids,
        **request.decision.model_dump(),
    )
    existing_decision = next((item for item in run.decisions if item.id == decision.id), None)
    if existing_decision is None:
        engine.record_decision(run_id, decision)
    else:
        decision = existing_decision

    current = engine.get_run(run_id)
    evaluation = engine.evaluate_run(
        run_id,
        {
            "case_id": current.case_id,
            "expected_state": "COMPLETED",
            "minimum_qualified_evidence": sum(item.qualification == "QUALIFIED" for item in current.evidence),
            "requires_claim": True,
            "requires_financial_analysis": True,
            "requires_valuation_scenarios": True,
            "minimum_red_team_reviews": 1,
            "required_ic_review_roles": list(MVP_IC_ROLES),
        },
    )
    return MvpWorkflowReceipt(
        case_id=current.case_id,
        run_id=current.id,
        state="COMPLETED",
        memo_status=current.memo.status if current.memo is not None else "UNKNOWN",
        financial_analysis_input_hash=analysis.input_hash,
        valuation_scenarios_id=valuation.id,
        red_team_review_id=red_team.id,
        ic_review_ids=ic_review_ids,
        decision_id=decision.id,
        evaluation=evaluation,
    )
