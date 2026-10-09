#!/usr/bin/env python3
"""Smoke-test a running Financial DeepResearch Runtime over HTTP.

The script intentionally uses only the Python standard library so it can run on
fresh developer machines and CI runners without installing project packages.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("RUNTIME_BASE_URL", "http://127.0.0.1:8011").rstrip("/")
API_KEY = os.environ.get("DEEPRESEARCH_API_KEY") or os.environ.get("SMOKE_API_KEY")


def _headers(actor: str | None = None, role: str | None = None) -> dict[str, str]:
    headers = {"accept": "application/json", "content-type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    if actor:
        headers["x-actor"] = actor
    if role:
        headers["x-actor-role"] = role
    return headers


def _request(method: str, path: str, payload: dict[str, Any] | None = None, *, actor: str | None = None, role: str | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(f"{BASE_URL}{path}", data=body, headers=_headers(actor, role), method=method)
    try:
        with urlopen(request, timeout=20) as response:
            data = response.read().decode("utf-8")
            return json.loads(data) if data else None
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"{method} {path} failed: {error}") from error


def _wait_ready() -> None:
    deadline = time.monotonic() + int(os.environ.get("SMOKE_READY_TIMEOUT_SECONDS", "120"))
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            ready = _request("GET", "/api/v1/ready")
            if ready.get("status") == "ready":
                print("ready: ok")
                return
        except Exception as error:  # noqa: BLE001 - surface last readiness error below
            last_error = error
        time.sleep(2)
    raise RuntimeError(f"runtime did not become ready: {last_error}")


def _qualified_evidence(run: dict[str, Any], stance: str) -> str:
    return next(
        item["id"]
        for item in run["evidence"]
        if item["stance"] == stance and item["qualification"] == "QUALIFIED"
    )


def _scenario(name: str, revenue_growth: str, margin: str, fcf_margin: str, evidence_id: str) -> dict[str, Any]:
    links = {
        "revenue_growth_pct": [evidence_id],
        "operating_margin_pct": [evidence_id],
        "fcf_margin_pct": [evidence_id],
        "discount_rate_pct": [evidence_id],
        "terminal_growth_pct": [evidence_id],
        "net_cash": [evidence_id],
        "shares_outstanding": [evidence_id],
    }
    return {
        "name": name,
        "revenue_growth_pct": revenue_growth,
        "operating_margin_pct": margin,
        "fcf_margin_pct": fcf_margin,
        "discount_rate_pct": "10",
        "terminal_growth_pct": "3",
        "net_cash": "10",
        "shares_outstanding": "100",
        "evidence_ids": links,
    }


def main() -> int:
    _wait_ready()
    created = _request(
        "POST",
        "/api/v1/research-cases",
        {"question": "Assess ACME's margin durability and downside risk", "target": "ACME"},
    )
    run_id = created["run_id"]
    print(f"created run: {run_id}")

    run = _request("POST", f"/api/v1/research-runs/{run_id}/execute", {})
    if run["state"] != "COMPLETED":
        raise RuntimeError(f"expected completed run, got {run['state']}")
    supporting = _qualified_evidence(run, "SUPPORTING")
    counter = _qualified_evidence(run, "COUNTER")
    thesis_id = run["thesis"]["id"]
    print("execute: completed")

    financial = _request(
        "POST",
        f"/api/v1/research-runs/{run_id}/financial-analysis",
        {
            "snapshot": {
                "period": "FY2025",
                "revenue": "120",
                "prior_revenue": "100",
                "operating_income": "24",
                "operating_cash_flow": "20",
                "capex": "5",
                "cash": "30",
                "debt": "20",
            },
            "evidence_ids": {
                "revenue": [supporting],
                "prior_revenue": [supporting],
                "operating_income": [supporting],
                "operating_cash_flow": [supporting],
                "capex": [supporting],
                "cash": [supporting],
                "debt": [supporting],
            },
        },
    )
    print(f"financial analysis: revenue growth {financial['revenue_growth_pct']}%")

    valuation = _request(
        "POST",
        f"/api/v1/research-runs/{run_id}/valuation-scenarios",
        {
            "base_revenue": "120",
            "base_revenue_evidence_ids": [supporting],
            "scenarios": [
                _scenario("BULL", "15", "25", "20", supporting),
                _scenario("BASE", "8", "20", "15", supporting),
                _scenario("BEAR", "0", "12", "8", supporting),
            ],
        },
    )
    print(f"valuation: {valuation['id']}")

    _request(
        "POST",
        f"/api/v1/research-runs/{run_id}/red-team-reviews",
        {
            "reviewer": "reviewer@example.com",
            "challenge": "The thesis may underweight qualified downside evidence.",
            "evidence_ids": [counter],
            "outcome": "SUPPORTED",
            "rationale": "Counter-evidence is material to the downside case.",
        },
        actor="reviewer@example.com",
        role="reviewer",
    )
    print("red-team review: ok")

    for ic_role in ("BULL", "BEAR", "FINANCIAL", "INDUSTRY", "PARTNER"):
        _request(
            "POST",
            f"/api/v1/research-runs/{run_id}/ic-reviews",
            {
                "role": ic_role,
                "reviewer": "reviewer@example.com",
                "position": "SUPPORTIVE" if ic_role == "BULL" else "MIXED",
                "recommendation": "APPROVE" if ic_role == "BULL" else "HOLD",
                "rationale": f"The {ic_role.lower()} review considered the evidence package.",
                "evidence_ids": [supporting],
            },
            actor="reviewer@example.com",
            role="reviewer",
        )
    print("ic reviews: ok")

    final_run = _request(
        "POST",
        f"/api/v1/research-runs/{run_id}/decisions",
        {
            "actor": "chair@example.com",
            "action": "APPROVE_THESIS",
            "target_id": thesis_id,
            "rationale": "Approved after memo, counter-evidence, valuation, and IC reviews were checked.",
        },
        actor="chair@example.com",
        role="chair",
    )
    print(f"decision: {final_run['decisions'][-1]['id']}")

    memo = _request("GET", f"/api/v1/research-runs/{run_id}/memo")
    if not memo.get("red_team_review_ids") or not memo.get("ic_review_ids"):
        raise RuntimeError("memo did not link reviews")
    if memo.get("valuation_scenarios_id") != valuation["id"]:
        raise RuntimeError("memo did not link valuation scenarios")
    print(f"memo: {memo['id']}")
    print("smoke: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - CLI should show concise failure
        print(f"smoke: failed: {error}", file=sys.stderr)
        raise SystemExit(1)
