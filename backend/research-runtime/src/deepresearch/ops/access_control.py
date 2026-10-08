"""Minimal request-level access control for write-side review actions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

ActorRole = str

_ALLOWED_ROLES: set[ActorRole] = {"analyst", "reviewer", "chair", "admin"}
_REVIEW_ROLES: set[ActorRole] = {"reviewer", "chair", "admin"}
_DECISION_ROLES: set[ActorRole] = {"chair", "admin"}


def _required_roles(path: str, method: str) -> set[ActorRole] | None:
    if method.upper() != "POST":
        return None
    if path.endswith("/red-team-reviews") or path.endswith("/ic-reviews"):
        return _REVIEW_ROLES
    if path.endswith("/decisions"):
        return _DECISION_ROLES
    return None


def _deny(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


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
        required_roles = _required_roles(request.url.path, request.method)
        if required_roles is None:
            return await call_next(request)

        actor = request.headers.get("x-actor", "").strip()
        role = request.headers.get("x-actor-role", "").strip().lower()
        if not actor or not role:
            return _deny(status.HTTP_401_UNAUTHORIZED, "X-Actor and X-Actor-Role are required")
        if role not in _ALLOWED_ROLES:
            return _deny(status.HTTP_403_FORBIDDEN, f"unsupported actor role: {role}")
        if role not in required_roles:
            return _deny(status.HTTP_403_FORBIDDEN, f"role {role} is not allowed for this action")

        request.state.actor = actor
        request.state.actor_role = role
        return await call_next(request)
