"""Replaceable research planning boundary."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchPlan, ResearchTask


def research_input_hash(case: ResearchCase) -> str:
    return sha256(f"{case.id}|{case.target}|{case.question}".encode()).hexdigest()


class ResearchPlanner(Protocol):
    name: str
    version: str

    def plan(self, case: ResearchCase) -> ResearchPlan: ...


class PlannerProviderError(RuntimeError):
    """An LLM transport or structured-output failure."""


class LLMPlannerDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[ResearchTask] = Field(min_length=1)


class LLMResearchPlanner:
    """OpenAI-compatible structured planner; model output remains untrusted."""

    version = "v1"

    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: float = 30.0) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be blank")
        if not base_url.strip():
            raise ValueError("base_url must not be blank")
        if not model.strip():
            raise ValueError("model must not be blank")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.name = f"llm:{model}"

    def plan(self, case: ResearchCase) -> ResearchPlan:
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "Return only JSON matching {tasks:[ResearchTask]}. Propose evidence-bearing financial research tasks, include counter-evidence, and do not state financial facts or conclusions.",
                    },
                    {"role": "user", "content": json.dumps(case.model_dump(mode="json"), sort_keys=True)},
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        request_hash = sha256(body).hexdigest()
        request = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise PlannerProviderError(f"planner provider returned HTTP {error.code}") from error
        except (URLError, TimeoutError, OSError) as error:
            raise PlannerProviderError(f"planner provider transport failed: {error}") from error
        response_hash = sha256(raw).hexdigest()
        try:
            envelope = json.loads(raw.decode("utf-8"))
            content = envelope["choices"][0]["message"]["content"]
            draft = LLMPlannerDraft.model_validate(json.loads(content))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValidationError) as error:
            raise PlannerProviderError(f"planner response contract invalid: {error}") from error
        return ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name=self.name,
            planner_version=self.version,
            input_hash=research_input_hash(case),
            tasks=draft.tasks,
            provenance={
                "provider": self.base_url,
                "model": self.model,
                "request_hash": request_hash,
                "response_hash": response_hash,
            },
        )


def create_configured_research_planner() -> ResearchPlanner:
    if os.environ.get("DEEPRESEARCH_PLANNER", "deterministic").strip().lower() != "llm":
        return DeterministicResearchPlanner()
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL") or os.environ.get("LLM_BASE_URL")
    model = os.environ.get("DEEPSEEK_MODEL") or os.environ.get("LLM_MODEL")
    missing = [name for name, value in (("DEEPSEEK_API_KEY", api_key), ("DEEPSEEK_BASE_URL", base_url), ("DEEPSEEK_MODEL", model)) if not value]
    if missing:
        raise ValueError(f"LLM planner configuration missing: {', '.join(missing)}")
    assert api_key is not None and base_url is not None and model is not None
    return LLMResearchPlanner(api_key, base_url, model)


class DeterministicResearchPlanner:
    """Local non-LLM planner used until a production planner is evaluated."""

    name = "deterministic-financial-planner"
    version = "v1"

    def plan(self, case: ResearchCase) -> ResearchPlan:
        tasks = [
            ResearchTask(
                id="market",
                title="Market structure",
                purpose="Assess market growth and competitive structure",
                tool_name="deterministic-research",
                evidence_requirements=[EvidenceRequirement(id="market-signal", description="market evidence")],
            ),
            ResearchTask(
                id="fundamentals",
                title="Financial fundamentals",
                purpose="Assess revenue, margin, cash flow and balance-sheet durability",
                tool_name="deterministic-research",
                evidence_requirements=[EvidenceRequirement(id="fundamental-signal", description="financial evidence")],
            ),
            ResearchTask(
                id="risk",
                title="Downside and disconfirming evidence",
                purpose="Test risks and conditions that would invalidate the thesis",
                depends_on=["market", "fundamentals"],
                tool_name="deterministic-research",
                evidence_requirements=[EvidenceRequirement(id="risk-signal", description="risk evidence", required_stances=["COUNTER"])],
            ),
        ]
        return ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name=self.name,
            planner_version=self.version,
            input_hash=research_input_hash(case),
            tasks=tasks,
        )
