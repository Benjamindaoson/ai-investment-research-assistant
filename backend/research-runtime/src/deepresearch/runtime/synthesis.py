"""Structured, replaceable claim and thesis synthesis boundary."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from deepresearch.domain.models import ResearchCase, ResearchRun


class SynthesisProviderError(RuntimeError):
    """An LLM transport or structured synthesis contract failure."""


class SynthesisClaimDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1, max_length=120)
    statement: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=100)
    confidence: float = Field(ge=0, le=1)


class SynthesisThesisDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: str = Field(min_length=3, max_length=5000)
    bull: str = Field(min_length=1, max_length=3000)
    base: str = Field(min_length=1, max_length=3000)
    bear: str = Field(min_length=1, max_length=3000)


class SynthesisDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: list[SynthesisClaimDraft] = Field(min_length=1, max_length=20)
    thesis: SynthesisThesisDraft
    provenance: dict[str, str] = Field(default_factory=dict)


class ResearchSynthesizer(Protocol):
    name: str
    version: str

    def synthesize(self, case: ResearchCase, run: ResearchRun) -> SynthesisDraft: ...


class DeterministicResearchSynthesizer:
    """Bounded local synthesis; it is not an investment recommendation."""

    name = "deterministic-evidence-synthesis"
    version = "v1"

    def synthesize(self, case: ResearchCase, run: ResearchRun) -> SynthesisDraft:
        claims: list[SynthesisClaimDraft] = []
        for task in run.tasks:
            observed = [record for record in run.evidence if record.task_id == task.id]
            qualified = [record for record in observed if record.qualification == "QUALIFIED"]
            stance_counts = ", ".join(
                f"{stance.lower()}={sum(record.stance == stance for record in observed)}"
                for stance in ("SUPPORTING", "COUNTER", "CONFLICTING")
            )
            claims.append(
                SynthesisClaimDraft(
                    task_id=task.id,
                    statement=(
                        f"{task.title}: {len(qualified)} of {len(observed)} observed evidence records qualified "
                        f"({stance_counts})."
                    ),
                    evidence_ids=list(dict.fromkeys(item.id for item in qualified)),
                    confidence=round(len(qualified) / len(observed), 4) if observed else 0.0,
                )
            )
        supporting = self._task_titles_with_stance(run, "SUPPORTING")
        downside = self._task_titles_with_stance(run, "COUNTER") + self._task_titles_with_stance(run, "CONFLICTING")
        unresolved = [
            f"{task.id}:{requirement.id}"
            for task in run.tasks
            for requirement in task.evidence_requirements
            if not self._requirement_is_qualified(run, task.id, requirement.id)
        ]
        qualified_count = sum(
            self._task_is_qualified(run, task.id) for task in run.tasks
        )
        unresolved_text = ", ".join(unresolved) or "none"
        return SynthesisDraft(
            claims=claims,
            thesis=SynthesisThesisDraft(
                statement=f"Observed evidence qualifies {qualified_count} of {len(run.tasks)} task claims; interpretation requires human review.",
                bull=f"Bull scenario: qualified supporting evidence is observed for {', '.join(supporting) or 'no task'}; assumptions remain subject to review.",
                base=f"Base scenario: {qualified_count} of {len(run.tasks)} task claims are qualified, with unresolved requirements {unresolved_text}.",
                bear=f"Bear scenario: qualified counter or conflicting evidence is observed for {', '.join(dict.fromkeys(downside)) or 'no task'}; unresolved requirements are {unresolved_text}.",
            ),
            provenance={"provider": self.name, "version": self.version, "case_id": case.id},
        )

    @staticmethod
    def _task_is_qualified(run: ResearchRun, task_id: str) -> bool:
        task = next(item for item in run.tasks if item.id == task_id)
        return all(
            sum(
                record.qualification == "QUALIFIED"
                for record in run.evidence
                if record.task_id == task.id and record.requirement_id == requirement.id
            )
            >= requirement.minimum_records
            for requirement in task.evidence_requirements
        )

    @classmethod
    def _requirement_is_qualified(cls, run: ResearchRun, task_id: str, requirement_id: str) -> bool:
        task = next(item for item in run.tasks if item.id == task_id)
        requirement = next(item for item in task.evidence_requirements if item.id == requirement_id)
        return sum(
            record.qualification == "QUALIFIED"
            for record in run.evidence
            if record.task_id == task_id and record.requirement_id == requirement_id
        ) >= requirement.minimum_records

    @staticmethod
    def _task_titles_with_stance(run: ResearchRun, stance: str) -> list[str]:
        return [
            task.title
            for task in run.tasks
            if any(
                record.task_id == task.id
                and record.stance == stance
                and record.qualification == "QUALIFIED"
                for record in run.evidence
            )
        ]


class LLMResearchSynthesizer:
    """OpenAI-compatible structured synthesizer; model output remains untrusted."""

    name = "llm-synthesis"
    version = "v1"

    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: float = 60.0) -> None:
        if not api_key.strip() or not base_url.strip() or not model.strip():
            raise ValueError("api_key, base_url, and model must not be blank")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def synthesize(self, case: ResearchCase, run: ResearchRun) -> SynthesisDraft:
        qualified = [record.model_dump(mode="json") for record in run.evidence if record.qualification == "QUALIFIED"]
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return only JSON with claims and thesis. Each task must have exactly one claim. "
                            "Only cite evidence IDs present in the supplied QUALIFIED evidence. "
                            "Use the evidence stance, including counter and conflicting evidence, in the scenarios. "
                            "Do not invent facts, citations, numbers, or evidence IDs. "
                            'Shape: {"claims":[{"task_id":"...","statement":"...",'
                            '"evidence_ids":["..."],"confidence":0.0}],"thesis":'
                            '{"statement":"...","bull":"...","base":"...","bear":"..."}}'
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "case": case.model_dump(mode="json"),
                                "tasks": [task.model_dump(mode="json") for task in run.tasks],
                                "qualified_evidence": qualified,
                            },
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
            headers={"accept": "application/json", "content-type": "application/json", "authorization": f"Bearer {self._api_key}"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise SynthesisProviderError(f"synthesis provider returned HTTP {error.code}") from error
        except (URLError, TimeoutError, OSError) as error:
            raise SynthesisProviderError(f"synthesis provider transport failed: {error}") from error
        try:
            envelope = json.loads(raw.decode("utf-8"))
            content = envelope["choices"][0]["message"]["content"]
            draft = SynthesisDraft.model_validate(json.loads(self._strip_json_fence(content)))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValidationError) as error:
            raise SynthesisProviderError(f"synthesis response contract invalid: {error}") from error
        return draft.model_copy(
            update={
                "provenance": {
                    "provider": self.base_url,
                    "model": self.model,
                    "request_hash": request_hash,
                    "response_hash": sha256(raw).hexdigest(),
                }
            }
        )

    @staticmethod
    def _strip_json_fence(content: object) -> str:
        if not isinstance(content, str):
            raise TypeError("synthesis message content must be a string")
        text = content.strip()
        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]).strip()
        return text


def create_configured_research_synthesizer() -> ResearchSynthesizer:
    if os.environ.get("DEEPRESEARCH_SYNTHESIZER", "deterministic").strip().lower() != "llm":
        return DeterministicResearchSynthesizer()
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL") or os.environ.get("LLM_BASE_URL")
    model = os.environ.get("DEEPSEEK_MODEL") or os.environ.get("LLM_MODEL")
    missing = [name for name, value in (("DEEPSEEK_API_KEY", api_key), ("DEEPSEEK_BASE_URL", base_url), ("DEEPSEEK_MODEL", model)) if not value]
    if missing:
        raise ValueError(f"LLM synthesizer configuration missing: {', '.join(missing)}")
    assert api_key is not None and base_url is not None and model is not None
    return LLMResearchSynthesizer(api_key, base_url, model)
