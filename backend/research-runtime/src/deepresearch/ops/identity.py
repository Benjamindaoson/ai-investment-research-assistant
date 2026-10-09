"""Signed runtime identity tokens for production write boundaries."""

from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
from typing import Any

_ALLOWED_ROLES = {"analyst", "reviewer", "chair", "admin"}


@dataclass(frozen=True)
class RuntimeIdentity:
    actor: str
    role: str
    subject: str | None = None
    organization_id: str | None = None
    workspace_id: str | None = None
    expires_at: int | None = None


def identity_signing_secret() -> str:
    return os.environ.get("DEEPRESEARCH_IDENTITY_SIGNING_SECRET", "").strip()


def signed_identity_required() -> bool:
    return bool(identity_signing_secret())


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_identity(identity: RuntimeIdentity, secret: str | None = None) -> str:
    """Return a compact HMAC token for ingress-signed actor identity.

    The token is not a full JWT and intentionally has no algorithm agility. It is
    a small deployment boundary for services that do not yet use SSO/JWT but need
    to prevent clients from freely forging actor headers.
    """

    signing_secret = (secret or identity_signing_secret()).strip()
    if not signing_secret:
        raise ValueError("identity signing secret is required")
    if identity.role not in _ALLOWED_ROLES:
        raise ValueError(f"unsupported actor role: {identity.role}")
    if not identity.actor.strip():
        raise ValueError("actor must not be blank")
    payload = {
        "actor": identity.actor.strip(),
        "role": identity.role,
        "sub": identity.subject,
        "org": identity.organization_id,
        "workspace": identity.workspace_id,
        "exp": identity.expires_at,
    }
    material = _b64url_encode(_canonical_json({key: value for key, value in payload.items() if value is not None}))
    signature = hmac_new(signing_secret.encode("utf-8"), material.encode("ascii"), sha256).digest()
    return f"{material}.{_b64url_encode(signature)}"


def verify_identity_token(token: str, secret: str | None = None, now: int | None = None) -> RuntimeIdentity:
    signing_secret = (secret or identity_signing_secret()).strip()
    if not signing_secret:
        raise ValueError("identity signing secret is required")
    try:
        material, supplied_signature = token.split(".", 1)
    except ValueError as error:
        raise ValueError("identity token must contain payload and signature") from error
    expected = _b64url_encode(hmac_new(signing_secret.encode("utf-8"), material.encode("ascii"), sha256).digest())
    if not compare_digest(supplied_signature, expected):
        raise ValueError("identity token signature is invalid")
    try:
        payload = json.loads(_b64url_decode(material).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("identity token payload is invalid") from error
    if not isinstance(payload, dict):
        raise ValueError("identity token payload must be an object")
    actor = str(payload.get("actor") or "").strip()
    role = str(payload.get("role") or "").strip().lower()
    if not actor:
        raise ValueError("identity token actor is missing")
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"unsupported actor role: {role}")
    exp = payload.get("exp")
    if exp is not None:
        try:
            expires_at = int(exp)
        except (TypeError, ValueError) as error:
            raise ValueError("identity token expiration is invalid") from error
        current = int(time.time()) if now is None else now
        if expires_at < current:
            raise ValueError("identity token has expired")
    else:
        expires_at = None
    return RuntimeIdentity(
        actor=actor,
        role=role,
        subject=str(payload["sub"]) if payload.get("sub") is not None else None,
        organization_id=str(payload["org"]) if payload.get("org") is not None else None,
        workspace_id=str(payload["workspace"]) if payload.get("workspace") is not None else None,
        expires_at=expires_at,
    )


def bearer_token(headers: Any) -> str | None:
    authorization = str(headers.get("authorization") or "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    token = str(headers.get("x-actor-token") or "").strip()
    return token or None
