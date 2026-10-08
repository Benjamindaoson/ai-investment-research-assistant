"""Minimal request-level access control for write-side review actions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

ActorRole = str

_ALLOWED_ROLES: set[ActorRole] = {"analyst", "reviewer", "chair", "admin"}
_REVIEW_ROLES: set[ActorRole] = {"reviewer", "chair", "admin"}
_DECISION_ROLES: set[ActorRole] = {"chair", "admin"}


def _policy(path: str, method: str) -> tuple[set[ActorRole], str] | None:
    if method.upper() != "POST":
        return None
    if path.endswith("/red-team-reviews") or path.endswith("/ic-reviews"):
        return _REVIEW_ROLES, "reviewer"
    if path.endswith("/decisions"):
        return _DECISION_ROLES, "actor"
    return None


def _deny(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def _json_object(request: Request) -> dict[str, Any] | None:
    try:
        payload = await request.json()
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


async def _identity_matches_request_body(request: Request, actor: str, identity_field: str) -> bool:
    payload = await _json_object(request)
    if payload is None:
        return True
    supplied = payload.get(identity_field)
    if supplied is None:
        return True
    return str(supplied).strip() == actor


def install_access_control(app: FastAPI) -> None:
    """Require actor headers for review and decision write routes.

    This is intentionally small and header-based so it works for local demos,
    Docker deployments, and test clients without introducing a full identity
    provider. A production deployment should replace this boundary with signed
    identity from the ingress, SSO, or API gateway.
    """

    @app.middleware("http")
    async def access_control(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        policy = _policy(request.url.path, request.method)
        if policy is None:
            return await call_next(request)
        required_roles, identity_field = policy

        actor = request.headers.get("x-actor", "").strip()
        role = request.headers.get("x-actor-role", "").strip().lower()
        if not actor or not role:
            return _deny(status.HTTP_401_UNAUTHORIZED, "X-Actor and X-Actor-Role are required")
        if role not in _ALLOWED_ROLES:
            return _deny(status.HTTP_403_FORBIDDEN, f"unsupported actor role: {role}")
        if role not in required_roles:
            return _deny(status.HTTP_403_FORBIDDEN, f"role {role} is not allowed for this action")
        if not await _identity_matches_request_body(request, actor, identity_field):
            return _deny(status.HTTP_403_FORBIDDEN, f"request field {identity_field} must match X-Actor")

        request.state.actor = actor
        request.state.actor_role = role
        return await call_next(request)
