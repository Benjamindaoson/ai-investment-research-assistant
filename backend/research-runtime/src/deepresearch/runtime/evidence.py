"""Evidence consumption boundary owned by FinEvidence in production."""

import json
from hashlib import sha256
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from deepresearch.domain.models import EvidenceRecord, ResearchCase, ResearchTask


class EvidenceProvider(Protocol):
    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]: ...


class EvidenceProviderError(RuntimeError):
    """A provider contract or transport failure that must remain observable."""


class EvidenceProviderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(ge=1)
    records: list[EvidenceRecord]


class HttpEvidenceProvider:
    """FinEvidence-compatible HTTP adapter; retrieval remains external."""

    name = "finevidence-http"

    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        if not base_url.strip():
            raise ValueError("base_url must not be blank")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]:
        payload = json.dumps(
            {
                "schema_version": 1,
                "task": task.model_dump(mode="json"),
                "case": case.model_dump(mode="json"),
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/v1/evidence/collect",
            data=payload,
            headers={"content-type": "application/json", "accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise EvidenceProviderError(f"provider returned HTTP {error.code}") from error
        except (URLError, TimeoutError, OSError) as error:
            raise EvidenceProviderError(f"provider transport failed: {error}") from error
        try:
            response = EvidenceProviderResponse.model_validate(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as error:
            raise EvidenceProviderError(f"provider response contract invalid: {error}") from error
        if response.schema_version != 1:
            raise EvidenceProviderError(f"unsupported provider schema version: {response.schema_version}")
        requirement_ids = {item.id for item in task.evidence_requirements}
        for record in response.records:
            if record.task_id != task.id or record.requirement_id not in requirement_ids:
                raise EvidenceProviderError("provider returned an evidence reference outside the requested task")
        return response.records


class DeterministicEvidenceProvider:
    """Local demo provider; it is not live market data or a substitute for FinEvidence."""

    name = "deterministic-demo"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]:
        self.calls.append(task.id)
        records: list[EvidenceRecord] = []
        for requirement in task.evidence_requirements:
            records.extend(
                [
                    EvidenceRecord(
                        task_id=task.id,
                        requirement_id=requirement.id,
                        stance="SUPPORTING",
                        source_id=f"demo-filing-{case.target.lower()}",
                        source_title=f"{case.target} public filing (deterministic fixture)",
                        excerpt=f"Fixture evidence for {task.title}: the observed signal supports the research question.",
                        provider=self.name,
                        source_url="https://example.invalid/fixtures/filing",
                        source_version="fixture-v1",
                        locator="fixture:1",
                        content_hash=sha256(f"supporting:{case.id}:{task.id}".encode()).hexdigest(),
                        provenance={"fixture": True, "case_id": case.id},
                    ),
                    EvidenceRecord(
                        task_id=task.id,
                        requirement_id=requirement.id,
                        stance="COUNTER",
                        source_id=f"demo-risk-{case.target.lower()}",
                        source_title=f"{case.target} risk disclosure (deterministic fixture)",
                        excerpt=f"Fixture counter-evidence for {task.title}: downside conditions remain material.",
                        provider=self.name,
                        source_url="https://example.invalid/fixtures/risk",
                        source_version="fixture-v1",
                        locator="fixture:2",
                        content_hash=sha256(f"counter:{case.id}:{task.id}".encode()).hexdigest(),
                        provenance={"fixture": True, "case_id": case.id},
                    ),
                ]
            )
        return records


def evidence_hash(evidence: list[EvidenceRecord]) -> str:
    material = "|".join(f"{item.id}:{item.qualification}:{item.stance}" for item in evidence)
    return sha256(material.encode()).hexdigest()
