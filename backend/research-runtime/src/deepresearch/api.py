"""Small HTTP boundary for the Financial DeepResearch Runtime."""

import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from deepresearch.domain.models import DecisionRecord, FinancialSnapshot, ResearchCase
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import (
    DeterministicEvidenceProvider,
    EvidenceProvider,
    HttpEvidenceProvider,
)
from deepresearch.runtime.financial import FinancialAnalysisTool
from deepresearch.runtime.planner import ResearchPlanner, create_configured_research_planner


class CreateCaseRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    target: str = Field(min_length=1, max_length=300)


class ExecuteRequest(BaseModel):
    stop_after_tasks: int | None = Field(default=None, ge=1, le=100)


class DecisionRequest(BaseModel):
    actor: str = Field(min_length=1, max_length=200)
    action: str
    target_id: str
    rationale: str = Field(min_length=3, max_length=4000)


def create_app(store: SQLiteStore | None = None, provider: EvidenceProvider | None = None, planner: ResearchPlanner | None = None) -> FastAPI:
    runtime_store = store or SQLiteStore(Path(".data/deepresearch.sqlite3"))
    configured_provider = provider
    if configured_provider is None:
        base_url = os.environ.get("FINEVIDENCE_BASE_URL")
        configured_provider = HttpEvidenceProvider(base_url) if base_url else DeterministicEvidenceProvider()
    engine = ResearchEngine(runtime_store, configured_provider, planner=planner or create_configured_research_planner())
    financial_analysis = FinancialAnalysisTool()
    app = FastAPI(title="Financial DeepResearch Runtime", version="0.1.0")

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "financial-deepresearch-runtime"}

    @app.post("/api/v1/financial-analysis")
    def analyze_financials(snapshot: FinancialSnapshot) -> dict[str, Any]:
        return financial_analysis.analyze(snapshot).model_dump(mode="json")

    @app.post("/api/v1/research-cases", status_code=status.HTTP_201_CREATED)
    def create_case(request: CreateCaseRequest) -> dict[str, str]:
        case = ResearchCase(id=f"case-{uuid4().hex[:10]}", question=request.question, target=request.target)
        run = engine.create_run(case)
        return {"case_id": case.id, "run_id": run.id}

    @app.get("/api/v1/research-cases/{case_id}")
    def get_case(case_id: str) -> dict[str, Any]:
        try:
            return engine.get_run(f"run-{case_id}").model_dump(mode="json")
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

    @app.post("/api/v1/research-runs/{run_id}/decisions")
    def decision(run_id: str, request: DecisionRequest) -> dict[str, Any]:
        try:
            value = DecisionRecord.model_validate(request.model_dump())
            return engine.record_decision(run_id, value).model_dump(mode="json")
        except KeyError as error:
            raise HTTPException(status_code=404, detail="research run not found") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    return app


app = create_app()
