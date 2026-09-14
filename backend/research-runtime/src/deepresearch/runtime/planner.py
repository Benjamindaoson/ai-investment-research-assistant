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
    payload = {
        "case_id": case.id,
        "target": case.target,
        "question": case.question,
        "mandate": case.mandate.model_dump(mode="json"),
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ResearchPlanner(Protocol):
    name: str
    version: str
    supports_dynamic_tasks: bool

    def plan(self, case: ResearchCase) -> ResearchPlan: ...

    def replan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan: ...


class PlannerProviderError(RuntimeError):
    """An LLM transport or structured-output failure."""


class LLMPlannerDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[ResearchTask] = Field(min_length=1, max_length=5)


class LLMResearchPlanner:
    """OpenAI-compatible structured planner; model output remains untrusted."""

    version = "v1"
    supports_dynamic_tasks = True

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
        return self._plan(case, [])

    def replan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        return self._plan(case, unresolved_requirement_ids)

    def _plan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return only one JSON object with this shape: "
                            '{"tasks":[{"id":"task-id","title":"...","purpose":"...",'
                            '"depends_on":[],"tool_name":"...","evidence_requirements":['
                            '{"id":"requirement-id","description":"...","minimum_records":1,'
                            '"required_stances":["SUPPORTING"],"fact_type":"RETRIEVED_FACT",'
                            '"role":"value","criticality":"CRITICAL",'
                            '"evidence_role":"VALUE_SUPPORT"}]}]} . '
                            "Use 3 to 5 tasks so the plan remains bounded. "
                            "Every task must include purpose, tool_name, and at least one evidence requirement. "
                            "tool_name must be one of research, evidence.search, external-evidence, "
                            "deterministic-research, or financial-table; prefer research for general evidence. "
                            "Every evidence requirement must include id, description, minimum_records, and "
                            "required_stances; use only SUPPORTING, COUNTER, or CONFLICTING for stances. "
                            "Use only CRITICAL, SUPPORTING, or OPTIONAL for criticality. Use only VALUE_SUPPORT, "
                            "COMPARISON_SUPPORT, DERIVATION_INPUT, EXPLANATION_SUPPORT, or CONTEXT_SUPPORT "
                            "for evidence_role; do not invent enum values such as HIGH or RISK_SIGNAL. Optional "
                            "semantic fields are fact_type (RETRIEVED_FACT, DERIVED_FACT, EXPLANATORY_FACT, "
                            "CONTEXT_FACT), role, entity, metric, period, criticality, and evidence_role. "
                            "Include at least one COUNTER requirement for downside or disconfirming evidence. "
                            "Do not include rationale, search_queries, sources, facts, claims, thesis, or conclusions. "
                            "Do not invent financial data. "
                            f"Prioritize these unresolved requirements when replanning: {json.dumps(sorted(unresolved_requirement_ids))}."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"case": case.model_dump(mode="json"), "unresolved_requirement_ids": sorted(unresolved_requirement_ids)},
                            sort_keys=True,
                        ),
                    },
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
            draft = LLMPlannerDraft.model_validate(json.loads(self._strip_json_fence(content)))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValidationError) as error:
            raise PlannerProviderError(f"planner response contract invalid: {error}") from error
        return ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name=self.name,
            planner_version=self.version,
            input_hash=research_input_hash(case),
            tasks=draft.tasks,
            mandate=case.mandate,
            provenance={
                "provider": self.base_url,
                "model": self.model,
                "request_hash": request_hash,
                "response_hash": response_hash,
                "replan_unresolved_requirement_ids": sorted(unresolved_requirement_ids),
                "mandate": case.mandate.model_dump(mode="json"),
            },
        )

    @staticmethod
    def _strip_json_fence(content: object) -> str:
        if not isinstance(content, str):
            raise TypeError("planner message content must be a string")
        text = content.strip()
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]).strip()
        return text


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
    supports_dynamic_tasks = False

    def plan(self, case: ResearchCase) -> ResearchPlan:
        return self._plan(case, [])

    def replan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        return self._plan(case, unresolved_requirement_ids)

    def _plan(self, case: ResearchCase, unresolved_requirement_ids: list[str]) -> ResearchPlan:
        tasks = [
            ResearchTask(
                id="market",
                title="Market structure",
                purpose="Assess market growth and competitive structure",
                tool_name="deterministic-research",
                evidence_requirements=[
                    EvidenceRequirement(
                        id="market-signal",
                        description="market structure and competitive evidence",
                        fact_type="EXPLANATORY_FACT",
                        role="market_structure",
                        criticality="SUPPORTING",
                        evidence_role="EXPLANATION_SUPPORT",
                    )
                ],
            ),
            ResearchTask(
                id="fundamentals",
                title="Financial fundamentals",
                purpose="Assess revenue, margin, cash flow and balance-sheet durability",
                tool_name="deterministic-research",
                evidence_requirements=[
                    EvidenceRequirement(
                        id="fundamental-signal",
                        description="financial fundamentals and durability evidence",
                        fact_type="RETRIEVED_FACT",
                        role="financial_fundamentals",
                        criticality="CRITICAL",
                        evidence_role="VALUE_SUPPORT",
                    )
                ],
            ),
            ResearchTask(
                id="risk",
                title="Downside and disconfirming evidence",
                purpose="Test risks and conditions that would invalidate the thesis",
                depends_on=["market", "fundamentals"],
                tool_name="deterministic-research",
                evidence_requirements=[
                    EvidenceRequirement(
                        id="risk-signal",
                        description="downside and disconfirming evidence",
                        required_stances=["COUNTER"],
                        fact_type="RETRIEVED_FACT",
                        role="downside_risk",
                        criticality="CRITICAL",
                        evidence_role="VALUE_SUPPORT",
                    )
                ],
            ),
        ]
        return ResearchPlan(
            case_id=case.id,
            question=case.question,
            planner_name=self.name,
            planner_version=self.version,
            input_hash=research_input_hash(case),
            tasks=tasks,
            mandate=case.mandate,
            provenance={
                "mandate": case.mandate.model_dump(mode="json"),
                **({"replan_unresolved_requirement_ids": sorted(unresolved_requirement_ids)} if unresolved_requirement_ids else {}),
            },
        )
