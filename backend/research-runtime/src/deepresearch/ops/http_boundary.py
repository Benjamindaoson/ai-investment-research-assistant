"""HTTP operational middleware for production-like runtime deployments."""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger("deepresearch.http")


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error


class _SlidingWindowLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit = limit_per_minute
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float) -> bool:
        if self.limit <= 0:
            return True
        window = self._events[key]
        cutoff = now - 60.0
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= self.limit:
            return False
        window.append(now)
        return True


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if forwarded:
        return forwarded
    if request.client is not None:
        return request.client.host
    return "unknown"


def _json_log(payload: dict[str, object]) -> None:
    logger.info(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _set_default_header(response: Response, name: str, value: str) -> None:
    if name not in response.headers:
        response.headers[name] = value


def install_http_boundary(app: FastAPI) -> None:
    """Attach request id, security headers, size limits, and optional rate limits."""

    max_body_bytes = _int_env("DEEPRESEARCH_MAX_BODY_BYTES", 1_000_000)
    limiter = _SlidingWindowLimiter(_int_env("DEEPRESEARCH_RATE_LIMIT_PER_MINUTE", 0))

    @app.middleware("http")
    async def http_boundary(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = time.perf_counter()
        request_id = request.headers.get("x-request-id") or f"req-{uuid4().hex}"
        request.state.request_id = request_id

        content_length = request.headers.get("content-length")
        if content_length is not None and int(content_length) > max_body_bytes:
            response: Response = JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "request body is too large", "request_id": request_id},
            )
        elif not limiter.allow(_client_key(request), time.time()):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "rate limit exceeded", "request_id": request_id},
            )
        else:
            response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        _set_default_header(response, "X-Content-Type-Options", "nosniff")
        _set_default_header(response, "Referrer-Policy", "no-referrer")
        _set_default_header(response, "X-Frame-Options", "DENY")
        _json_log(
            {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            }
        )
        return response
