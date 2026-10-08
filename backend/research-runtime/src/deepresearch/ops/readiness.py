"""Deployment readiness checks for the Financial DeepResearch Runtime."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse


def _ok(detail: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"status": "ok"}
    if detail is not None:
        payload["detail"] = detail
    return payload


def _failed(error: Exception) -> dict[str, object]:
    return {"status": "failed", "error_type": type(error).__name__, "error": str(error)[:500]}


def _queue_check(queue: object | None) -> dict[str, object]:
    if queue is None:
        return _ok("database-scan")
    client = getattr(queue, "client", None)
    if client is not None and hasattr(client, "ping"):
        client.ping()
    return _ok(type(queue).__name__)


def readiness_snapshot(app: FastAPI) -> tuple[int, dict[str, Any]]:
    """Return readiness status and payload without depending on HTTP."""

    checks: dict[str, dict[str, object]] = {}
    engine = getattr(app.state, "research_engine", None)
    if engine is None:
        checks["engine"] = {"status": "failed", "error": "research engine missing from app.state"}
        return status.HTTP_503_SERVICE_UNAVAILABLE, {"status": "not_ready", "checks": checks}

    checks["engine"] = _ok(type(engine).__name__)
    try:
        engine.store.list_cases()
        checks["store"] = _ok(type(engine.store).__name__)
    except Exception as error:  # pragma: no cover - exact backend depends on deployment
        checks["store"] = _failed(error)

    try:
        checks["queue"] = _queue_check(getattr(engine, "run_queue", None))
    except Exception as error:  # pragma: no cover - exact backend depends on deployment
        checks["queue"] = _failed(error)

    try:
        tool_names = sorted(getattr(engine.tool_registry, "names"))
        if not tool_names:
            raise RuntimeError("tool registry is empty")
        checks["tools"] = _ok(tool_names)
    except Exception as error:
        checks["tools"] = _failed(error)

    try:
        planner = engine.planner
        checks["planner"] = _ok(f"{planner.name} · {planner.version}")
    except Exception as error:
        checks["planner"] = _failed(error)

    try:
        synthesizer = engine.synthesizer
        checks["synthesizer"] = _ok(f"{synthesizer.name} · {synthesizer.version}")
    except Exception as error:
        checks["synthesizer"] = _failed(error)

    reliability_loaded = bool(getattr(engine.__class__, "_reliability_patch_applied", False))
    checks["reliability_layer"] = _ok("loaded") if reliability_loaded else {
        "status": "failed",
        "error": "ResearchEngine reliability patch is not loaded",
    }

    ready = all(check.get("status") == "ok" for check in checks.values())
    return (
        status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        {"status": "ready" if ready else "not_ready", "checks": checks},
    )


def install_readiness(app: FastAPI) -> None:
    """Attach production readiness route to a FastAPI app."""

    @app.get("/api/v1/ready")
    def ready() -> JSONResponse:
        status_code, payload = readiness_snapshot(app)
        return JSONResponse(status_code=status_code, content=payload)
