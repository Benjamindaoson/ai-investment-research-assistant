"""Persistent audit logging for runtime write operations."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response


def _is_postgres_store(store: object) -> bool:
    return type(store).__name__ == "PostgresStore"


def _placeholder(store: object) -> str:
    return "%s" if _is_postgres_store(store) else "?"


def ensure_audit_log(store: object) -> None:
    """Create the audit table using store transaction semantics."""

    transaction = getattr(store, "_transaction")
    with transaction() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                occurred_at TEXT NOT NULL,
                request_id TEXT,
                actor TEXT,
                actor_role TEXT,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_id TEXT,
                status_code INTEGER NOT NULL,
                detail TEXT NOT NULL
            )
            """
        )


def record_audit_event(store: object, event: dict[str, Any]) -> None:
    ensure_audit_log(store)
    p = _placeholder(store)
    sql = (
        "INSERT INTO audit_events(id, occurred_at, request_id, actor, actor_role, method, path, action, "
        f"resource_id, status_code, detail) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})"
    )
    transaction = getattr(store, "_transaction")
    with transaction() as connection:
        connection.execute(
            sql,
            (
                event["id"],
                event["occurred_at"],
                event.get("request_id"),
                event.get("actor"),
                event.get("actor_role"),
                event["method"],
                event["path"],
                event["action"],
                event.get("resource_id"),
                event["status_code"],
                json.dumps(event.get("detail", {}), sort_keys=True),
            ),
        )


def list_audit_events(store: object, limit: int = 100) -> list[dict[str, Any]]:
    ensure_audit_log(store)
    p = _placeholder(store)
    transaction = getattr(store, "_transaction")
    with transaction() as connection:
        rows = connection.execute(
            f"SELECT * FROM audit_events ORDER BY occurred_at DESC LIMIT {p}",
            (max(1, min(limit, 500)),),
        ).fetchall()
    events: list[dict[str, Any]] = []
    for row in rows:
        payload = dict(row)
        detail = payload.get("detail")
        payload["detail"] = json.loads(detail) if isinstance(detail, str) and detail else {}
        events.append(payload)
    return events


def _audit_action(path: str, method: str) -> str | None:
    if method.upper() != "POST" or not path.startswith("/api/v1/"):
        return None
    if path.endswith("/execute"):
        return "execute_run"
    if path.endswith("/enqueue"):
        return "enqueue_run"
    if path.endswith("/replan"):
        return "replan_run"
    if path.endswith("/cancel"):
        return "cancel_run"
    if path.endswith("/financial-analysis"):
        return "record_financial_analysis"
    if path.endswith("/financial-facts"):
        return "record_financial_facts"
    if path.endswith("/valuation-scenarios"):
        return "record_valuation_scenarios"
    if path.endswith("/red-team-reviews"):
        return "record_red_team_review"
    if path.endswith("/ic-reviews"):
        return "record_ic_review"
    if path.endswith("/decisions"):
        return "record_decision"
    if path.endswith("/mvp-complete"):
        return "complete_mvp_workflow"
    if path.endswith("/research-cases"):
        return "create_research_case"
    return "api_write"


def _resource_id(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if "research-runs" in parts:
        index = parts.index("research-runs")
        if index + 1 < len(parts):
            return parts[index + 1]
    if "research-cases" in parts:
        index = parts.index("research-cases")
        if index + 1 < len(parts):
            return parts[index + 1]
    return None


def install_audit_log(app: FastAPI) -> None:
    """Persist write-side runtime audit events and expose a bounded query route."""

    @app.get("/api/v1/audit-events")
    def get_audit_events(limit: int = 100) -> JSONResponse:
        engine = getattr(app.state, "research_engine", None)
        if engine is None:
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": "research engine missing"})
        return JSONResponse(content=list_audit_events(engine.store, limit=limit))

    @app.middleware("http")
    async def audit_log(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        action = _audit_action(request.url.path, request.method)
        response = await call_next(request)
        if action is None:
            return response
        engine = getattr(request.app.state, "research_engine", None)
        if engine is None:
            return response
        try:
            record_audit_event(
                engine.store,
                {
                    "id": f"audit-{uuid4().hex}",
                    "occurred_at": datetime.now(UTC).isoformat(),
                    "request_id": getattr(request.state, "request_id", None),
                    "actor": getattr(request.state, "actor", None),
                    "actor_role": getattr(request.state, "actor_role", None),
                    "method": request.method,
                    "path": request.url.path,
                    "action": action,
                    "resource_id": _resource_id(request.url.path),
                    "status_code": response.status_code,
                    "detail": {
                        "organization_id": getattr(request.state, "organization_id", None),
                        "workspace_id": getattr(request.state, "workspace_id", None),
                    },
                },
            )
        except Exception:  # pragma: no cover - audit must not mask user-facing response
            return response
        return response
