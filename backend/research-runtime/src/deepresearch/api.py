"""Small HTTP boundary for the Financial DeepResearch Runtime."""

import os
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

from deepresearch.domain.models import (
    DecisionRecord,
    FinancialFactSet,
    FinancialSnapshot,
    InvestmentCommitteeReview,
    RedTeamReview,
    ResearchCase,
    ResearchMandate,
    ScenarioValuationInput,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine, RunLeaseConflictError, RunLeaseLostError
from deepresearch.runtime.evidence import (
    DeterministicEvidenceProvider,
    EvidenceProvider,
    HttpEvidenceProvider,
    HttpTableEvidenceProvider,
)
from deepresearch.runtime.financial import (
    FinancialAnalysisTool,
    ScenarioValuationTool,
    financial_snapshot_from_facts,
)
from deepresearch.runtime.mvp import (
    MvpWorkflowIncompleteError,
    MvpWorkflowRequest,
    complete_mvp_workflow,
)
from deepresearch.runtime.planner import (
    PlannerProviderError,
    ResearchPlanner,
    create_configured_research_planner,
)
from deepresearch.runtime.synthesis import (
    ResearchSynthesizer,
    create_configured_research_synthesizer,
)
from deepresearch.runtime.tools import ResearchToolRegistry


class CreateCaseRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    target: str = Field(min_length=1, max_length=300)
    mandate: ResearchMandate = Field(default_factory=ResearchMandate)


class ExecuteRequest(BaseModel):
    stop_after_tasks: int | None = Field(default=None, ge=1, le=100)


class EvaluateRequest(BaseModel):
    case: dict[str, Any]


class ResolveToolAttemptRequest(BaseModel):
    action: Literal["RETRY", "MARK_FAILED"]


class CancelRequest(BaseModel):
    reason: str = Field(default="Analyst requested cancellation.", min_length=3, max_length=500)


class DecisionRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=200)
    action: str
    target_id: str
    rationale: str = Field(min_length=3, max_length=4000)
    review_ids: list[str] = Field(default_factory=list, max_length=100)


class RedTeamReviewRequest(BaseModel):
    reviewer: str = Field(min_length=1, max_length=200)
    challenge: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=100)
    outcome: Literal["OPEN", "SUPPORTED", "REJECTED", "REQUIRES_RESEARCH"] = "OPEN"
    rationale: str = Field(min_length=3, max_length=4000)


class InvestmentCommitteeReviewRequest(BaseModel):
    role: Literal["BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER"]
    reviewer: str = Field(min_length=1, max_length=200)
    position: Literal["SUPPORTIVE", "CHALLENGING", "MIXED", "INSUFFICIENT"]
    recommendation: Literal["APPROVE", "HOLD", "REJECT", "REQUEST_RESEARCH"]
    rationale: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=100)


class EvidenceLinkedFinancialAnalysisRequest(BaseModel):
    snapshot: FinancialSnapshot
    evidence_ids: dict[str, list[str]] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_evidence_links(self) -> "EvidenceLinkedFinancialAnalysisRequest":
        allowed = set(FinancialSnapshot.model_fields) - {"period"}
        supplied = {
            key for key, value in self.snapshot.model_dump().items() if key != "period" and value is not None
        }
        unknown = set(self.evidence_ids) - allowed
        missing = supplied - set(self.evidence_ids)
        unused = set(self.evidence_ids) - supplied
        empty = {key for key, ids in self.evidence_ids.items() if not ids}
        if unknown:
            raise ValueError(f"unknown financial evidence fields: {sorted(unknown)}")
        if missing:
            raise ValueError(f"missing evidence links for financial fields: {sorted(missing)}")
        if unused:
            raise ValueError(f"evidence links require supplied financial fields: {sorted(unused)}")
        if empty:
            raise ValueError(f"financial evidence links must not be empty: {sorted(empty)}")
        return self


def create_app(
    store: SQLiteStore | None = None,
    provider: EvidenceProvider | None = None,
    planner: ResearchPlanner | None = None,
    synthesizer: ResearchSynthesizer | None = None,
    tool_registry: ResearchToolRegistry | None = None,
) -> FastAPI:
    runtime_store = store or SQLiteStore(Path(".data/deepresearch.sqlite3"))
    configured_provider = provider
    if configured_provider is None:
        base_url = os.environ.get("FIN_EVIDENCE_BASE_URL") or os.environ.get("FINEVIDENCE_BASE_URL")
        timeout = float(os.environ.get("FIN_EVIDENCE_TIMEOUT_SECONDS") or os.environ.get("FINEVIDENCE_TIMEOUT_SECONDS", "120"))
        configured_provider = HttpEvidenceProvider(base_url, timeout) if base_url else DeterministicEvidenceProvider()
    configured_registry = tool_registry
    if configured_registry is None and isinstance(configured_provider, HttpEvidenceProvider) and hasattr(configured_provider, "client"):
        configured_registry = ResearchToolRegistry(
            {
                **{
                    name: configured_provider
                    for name in ("deterministic-research", "external-evidence", "research", "evidence.search")
                },
                "financial-table": HttpTableEvidenceProvider(configured_provider.client),
            }
        )
    lease_seconds = float(os.environ.get("RESEARCH_RUNTIME_LEASE_SECONDS", "300"))
    configured_planner = planner or create_configured_research_planner()
    configured_synthesizer = synthesizer or create_configured_research_synthesizer()
    engine = ResearchEngine(
        runtime_store,
        configured_provider,
        planner=configured_planner,
        synthesizer=configured_synthesizer,
        tool_registry=configured_registry,
        lease_seconds=lease_seconds,
    )
    financial_analysis = FinancialAnalysisTool()
    valuation_scenarios = ScenarioValuationTool()
    app = FastAPI(title="Financial DeepResearch Runtime", version="0.1.0")
    app.state.research_engine = engine
    cors_origins = [
        origin.strip()
        for origin in os.environ.get(
            "RESEARCH_RUNTIME_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health")
    def health() -> dict[str, Any]:
        authority = getattr(configured_provider, "qualification_authority", "custom")
        evidence_mode = {"external": "LIVE_EXTERNAL", "runtime": "DETERMINISTIC_FIXTURE"}.get(authority, "CUSTOM")
        return {
            "status": "ok",
            "service": "financial-deepresearch-runtime",
            "evidence_mode": evidence_mode,
            "evidence_provider": getattr(configured_provider, "name", type(configured_provider).__name__),
            "planner": f"{configured_planner.name} · {configured_planner.version}",
            "synthesizer": f"{configured_synthesizer.name} · {configured_synthesizer.version}",
            "tools": list((configured_registry or ResearchToolRegistry.from_provider(configured_provider)).names),
        }

    @app.post("/api/v1/financial-analysis")
    def analyze_financials(snapshot: FinancialSnapshot) -> dict[str, Any]:
        return financial_analysis.analyze(snapshot).model_dump(mode="json")

    @app.post("/api/v1/research-runs/{run_id}/financial-facts")
    def analyze_run_financial_facts(run_id: str, request: FinancialFactSet) -> dict[str, Any]:
        try:
            snapshot, evidence_ids = financial_snapshot_from_facts(request)
            analysis = financial_analysis.analyze(snapshot, evidence_ids).model_copy(
                update={"financial_facts": request.facts}
            )
            engine.record_financial_analysis(run_id, analysis)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return analysis.model_dump(mode="json")

    @app.post("/api/v1/research-runs/{run_id}/financial-analysis")
    def analyze_run_financials(run_id: str, request: EvidenceLinkedFinancialAnalysisRequest) -> dict[str, Any]:
        try:
            analysis = financial_analysis.analyze(request.snapshot, request.evidence_ids)
            engine.record_financial_analysis(run_id, analysis)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return analysis.model_dump(mode="json")

    @app.get("/api/v1/research-runs/{run_id}/financial-analysis")
    def get_run_financials(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_financial_analysis(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research financial analysis not found") from error

    @app.post("/api/v1/research-runs/{run_id}/valuation-scenarios")
    def analyze_run_valuation_scenarios(run_id: str, request: ScenarioValuationInput) -> dict[str, Any]:
        try:
            run = engine.get_run(run_id)
            result = valuation_scenarios.analyze(run_id, run.case_id, request)
            engine.record_valuation_scenarios(run_id, result)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return result.model_dump(mode="json")

    @app.get("/api/v1/research-runs/{run_id}/valuation-scenarios")
    def get_run_valuation_scenarios(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_valuation_scenarios(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research valuation scenarios not found") from error

    @app.post("/api/v1/research-cases", status_code=status.HTTP_201_CREATED)
    def create_case(request: CreateCaseRequest) -> dict[str, str]:
        case = ResearchCase(
            id=f"case-{uuid4().hex[:10]}",
            question=request.question,
            target=request.target,
            mandate=request.mandate,
        )
        try:
            run = engine.create_run(case)
        except PlannerProviderError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return {"case_id": case.id, "run_id": run.id}

    @app.get("/api/v1/research-cases")
    def list_cases() -> list[dict[str, Any]]:
        return [case.model_dump(mode="json") for case in engine.list_cases()]

    @app.post("/api/v1/research-cases/{case_id}/runs", status_code=status.HTTP_201_CREATED)
    def create_case_run(case_id: str) -> dict[str, str]:
        try:
            case = engine.get_case(case_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research case not found") from error
        try:
            run = engine.create_run(case)
        except PlannerProviderError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return {"case_id": case.id, "run_id": run.id}

    @app.get("/api/v1/research-cases/{case_id}/runs")
    def list_case_runs(case_id: str) -> list[dict[str, Any]]:
        try:
            engine.get_case(case_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research case not found") from error
        return [run.model_dump(mode="json") for run in engine.list_runs(case_id)]

    @app.get("/api/v1/research-cases/{case_id}")
    def get_case(case_id: str) -> dict[str, Any]:
        try:
            return engine.get_case(case_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research case not found") from error

    @app.get("/api/v1/research-runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_run(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    @app.get("/api/v1/research-runs/{run_id}/plan")
    def plan(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_plan(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    @app.post("/api/v1/research-runs/{run_id}/execute")
    def execute(run_id: str, request: ExecuteRequest | None = None) -> dict[str, Any]:
        try:
            return engine.execute(run_id, request.stop_after_tasks if request else None).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except RunLeaseConflictError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except RunLeaseLostError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.post("/api/v1/research-runs/{run_id}/enqueue")
    def enqueue(run_id: str) -> JSONResponse:
        try:
            run = engine.enqueue(run_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        queued = run.state in {"CREATED", "PARTIAL"}
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED if queued else status.HTTP_200_OK,
            content={"run_id": run.id, "state": run.state, "queued": queued},
        )

    @app.post("/api/v1/research-runs/{run_id}/mvp-complete")
    def complete_mvp(run_id: str, request: MvpWorkflowRequest) -> dict[str, Any]:
        try:
            return complete_mvp_workflow(
                engine,
                financial_analysis,
                valuation_scenarios,
                run_id,
                request,
            ).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except MvpWorkflowIncompleteError as error:
            raise HTTPException(status_code=409, detail={"message": str(error), "state": error.state}) from error
        except (RunLeaseConflictError, RunLeaseLostError) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.post("/api/v1/research-runs/{run_id}/replan")
    def replan(run_id: str) -> dict[str, Any]:
        try:
            return engine.replan(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except PlannerProviderError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.post("/api/v1/research-runs/{run_id}/cancel")
    def cancel(run_id: str, request: CancelRequest | None = None) -> dict[str, Any]:
        try:
            reason = request.reason if request else "Analyst requested cancellation."
            return engine.cancel(run_id, reason).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    @app.post("/api/v1/research-runs/{run_id}/evaluate")
    def evaluate(run_id: str, request: EvaluateRequest) -> dict[str, Any]:
        try:
            return engine.evaluate_run(run_id, request.case).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.post("/api/v1/research-runs/{run_id}/tool-attempts/{attempt_id}/resolve")
    def resolve_tool_attempt(run_id: str, attempt_id: str, request: ResolveToolAttemptRequest) -> dict[str, Any]:
        try:
            return engine.resolve_tool_attempt(run_id, attempt_id, request.action).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/research-runs/{run_id}/evaluation")
    def evaluation(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_latest_evaluation(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="evaluation not found") from error

    @app.get("/api/v1/research-runs/{run_id}/events")
    def events(run_id: str) -> list[dict[str, Any]]:
        if runtime_store.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="research run not found")
        return runtime_store.events(run_id)

    @app.get("/api/v1/research-runs/{run_id}/trace")
    def trace(run_id: str) -> dict[str, object]:
        try:
            return engine.trace(run_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    @app.get("/api/v1/research-runs/{run_id}/memo")
    def memo(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_memo(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research memo not found") from error

    @app.get("/api/v1/research-runs/{run_id}/memory")
    def run_memory(run_id: str) -> dict[str, Any]:
        try:
            return engine.get_memory_for_run(run_id).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="investment memory not found") from error

    @app.get("/api/v1/investment-memory/{target}")
    def memory(target: str) -> dict[str, Any]:
        try:
            return engine.get_memory(target).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="investment memory not found") from error

    @app.post("/api/v1/research-runs/{run_id}/decisions")
    def decision(run_id: str, request: DecisionRequest) -> dict[str, Any]:
        try:
            value = DecisionRecord.model_validate(request.model_dump())
            return engine.record_decision(run_id, value).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.post("/api/v1/research-runs/{run_id}/red-team-reviews")
    def red_team_review(run_id: str, request: RedTeamReviewRequest) -> dict[str, Any]:
        try:
            run = engine.get_run(run_id)
            if run.thesis is None:
                raise ValueError("red-team review requires a synthesized thesis")
            review = RedTeamReview(
                run_id=run_id,
                thesis_id=run.thesis.id,
                reviewer=request.reviewer,
                challenge=request.challenge,
                evidence_ids=request.evidence_ids,
                outcome=request.outcome,
                rationale=request.rationale,
            )
            return engine.record_red_team_review(run_id, review).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/research-runs/{run_id}/red-team-reviews")
    def get_red_team_reviews(run_id: str) -> list[dict[str, Any]]:
        try:
            return [review.model_dump(mode="json") for review in engine.get_red_team_reviews(run_id)]
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    @app.post("/api/v1/research-runs/{run_id}/ic-reviews")
    def ic_review(run_id: str, request: InvestmentCommitteeReviewRequest) -> dict[str, Any]:
        try:
            run = engine.get_run(run_id)
            if run.thesis is None:
                raise ValueError("IC review requires a synthesized thesis")
            review = InvestmentCommitteeReview(
                run_id=run_id,
                thesis_id=run.thesis.id,
                role=request.role,
                reviewer=request.reviewer,
                position=request.position,
                recommendation=request.recommendation,
                rationale=request.rationale,
                evidence_ids=request.evidence_ids,
            )
            return engine.record_ic_review(run_id, review).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/api/v1/research-runs/{run_id}/ic-reviews")
    def get_ic_reviews(run_id: str) -> list[dict[str, Any]]:
        try:
            return [review.model_dump(mode="json") for review in engine.get_ic_reviews(run_id)]
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error

    return app


app = create_app()
