"""Small HTTP boundary for the Financial DeepResearch Runtime."""

import os
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from deepresearch.domain.models import (
    DecisionRecord,
    FinancialSnapshot,
    RedTeamReview,
    ResearchCase,
    ResearchMandate,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import (
    DeterministicEvidenceProvider,
    EvidenceProvider,
    HttpEvidenceProvider,
)
from deepresearch.runtime.financial import FinancialAnalysisTool
from deepresearch.runtime.planner import (
    PlannerProviderError,
    ResearchPlanner,
    create_configured_research_planner,
)


class CreateCaseRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    target: str = Field(min_length=1, max_length=300)
    mandate: ResearchMandate = Field(default_factory=ResearchMandate)


class ExecuteRequest(BaseModel):
    stop_after_tasks: int | None = Field(default=None, ge=1, le=100)


class CancelRequest(BaseModel):
    reason: str = Field(default="Analyst requested cancellation.", min_length=3, max_length=500)


class DecisionRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=200)
    action: str
    target_id: str
    rationale: str = Field(min_length=3, max_length=4000)


class RedTeamReviewRequest(BaseModel):
    reviewer: str = Field(min_length=1, max_length=200)
    challenge: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=100)
    outcome: Literal["OPEN", "SUPPORTED", "REJECTED", "REQUIRES_RESEARCH"] = "OPEN"
    rationale: str = Field(min_length=3, max_length=4000)


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


def create_app(store: SQLiteStore | None = None, provider: EvidenceProvider | None = None, planner: ResearchPlanner | None = None) -> FastAPI:
    runtime_store = store or SQLiteStore(Path(".data/deepresearch.sqlite3"))
    configured_provider = provider
    if configured_provider is None:
        base_url = os.environ.get("FIN_EVIDENCE_BASE_URL") or os.environ.get("FINEVIDENCE_BASE_URL")
        timeout = float(os.environ.get("FIN_EVIDENCE_TIMEOUT_SECONDS") or os.environ.get("FINEVIDENCE_TIMEOUT_SECONDS", "120"))
        configured_provider = HttpEvidenceProvider(base_url, timeout) if base_url else DeterministicEvidenceProvider()
    engine = ResearchEngine(runtime_store, configured_provider, planner=planner or create_configured_research_planner())
    financial_analysis = FinancialAnalysisTool()
    app = FastAPI(title="Financial DeepResearch Runtime", version="0.1.0")
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
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "financial-deepresearch-runtime"}

    @app.post("/api/v1/financial-analysis")
    def analyze_financials(snapshot: FinancialSnapshot) -> dict[str, Any]:
        return financial_analysis.analyze(snapshot).model_dump(mode="json")

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

    return app


app = create_app()
