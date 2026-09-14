"""Evidence consumption boundary owned by the external FinEvidence service."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Literal, Protocol, TypeVar
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from deepresearch.domain.models import (
    EvidenceRecord,
    EvidenceRequirement,
    ResearchCase,
    ResearchTask,
)


class EvidenceProvider(Protocol):
    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]: ...


class EvidenceProviderError(RuntimeError):
    """A provider contract or transport failure that must remain observable."""


WireModel = TypeVar("WireModel", bound=BaseModel)


class _WireModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FinEvidenceFilters(_WireModel):
    document_id: str | None = None
    source_type: Literal["text", "table", "image", "equation"] | None = None
    entity: str | None = None
    metric: str | None = None
    period: str | None = None
    tenant_id: str | None = None
    user_role: str | None = None


class FinEvidenceVerification(_WireModel):
    evidence_type: Literal["TEXT", "TABLE_CELL", "IMAGE", "EQUATION"]
    confidence: float = Field(ge=0.0, le=1.0)
    coverage_status: Literal["RETRIEVED", "SUPPORTED", "PARTIAL", "UNSUPPORTED", "UNVERIFIED"]


class FinEvidenceContent(_WireModel):
    text: str | None = None
    table: dict[str, Any] | None = None
    visual_reference: dict[str, Any] | None = None


class FinEvidenceProvenance(_WireModel):
    document_name: str
    page_number: int = Field(ge=1)
    source_url: str = Field(min_length=1)
    document_hash: str | None = None


class FinEvidenceStructure(_WireModel):
    table_id: str | None = None
    row_id: str | None = None
    column_id: str | None = None
    bbox: tuple[float, float, float, float] | None = None


class FinEvidenceFinancial(_WireModel):
    entity: str | None = None
    metric: str | None = None
    period: str | None = None
    unit: str | None = None
    category: str | None = None


class FinEvidenceObject(_WireModel):
    api_version: Literal["v1"] = "v1"
    evidence_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    source_type: Literal["text", "table_cell", "page_image", "equation"]
    score: float | None = None
    content: FinEvidenceContent
    provenance: FinEvidenceProvenance
    financial: FinEvidenceFinancial
    structure: FinEvidenceStructure
    verification: FinEvidenceVerification


class FinEvidenceSearchResponse(_WireModel):
    api_version: Literal["v1"] = "v1"
    evidence: list[FinEvidenceObject]
    catalog_size: int = Field(ge=0)


class FinEvidenceCoverageResponse(_WireModel):
    api_version: Literal["v1"] = "v1"
    coverage_score: float
    independent_coverage: float
    critical_coverage: float
    missing_requirements: list[str]
    status: Literal["ELIGIBLE", "PARTIAL", "INSUFFICIENT"]
    evidence: list[FinEvidenceObject]


class FinEvidenceTableResponse(_WireModel):
    api_version: Literal["v1"] = "v1"
    evidence: list[FinEvidenceObject]


class FinEvidenceVerifyResponse(_WireModel):
    api_version: Literal["v1"] = "v1"
    supported: bool
    coverage_score: float
    missing_requirements: list[str]
    supporting_evidence: list[FinEvidenceObject]


class FinEvidenceCitation(_WireModel):
    api_version: Literal["v1"] = "v1"
    evidence_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    document_name: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    source_url: str = Field(min_length=1)
    document_hash: str | None = None
    table_id: str | None = None
    row_id: str | None = None
    column_id: str | None = None
    bbox: tuple[float, float, float, float] | None = None


class FinEvidenceHealth(_WireModel):
    status: Literal["ok"]
    catalog_size: int = Field(ge=0)


class FinEvidenceClient:
    """Small typed client for the frozen FinEvidence Evidence Backend v1 API."""

    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        if not base_url.strip():
            raise ValueError("base_url must not be blank")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(self, path: str, model: type[WireModel], payload: dict[str, Any] | None = None) -> WireModel:
        data = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"content-type": "application/json", "accept": "application/json"},
            method="POST" if data is not None else "GET",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise EvidenceProviderError(f"provider returned HTTP {error.code} from {path}") from error
        except (URLError, TimeoutError, OSError) as error:
            raise EvidenceProviderError(f"provider transport failed at {path}: {error}") from error
        try:
            decoded = json.loads(raw.decode("utf-8"))
            return model.model_validate(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as error:
            raise EvidenceProviderError(f"provider response contract invalid at {path}: {error}") from error

    def health(self) -> FinEvidenceHealth:
        return self._request("/health", FinEvidenceHealth)

    def search(
        self,
        query: str,
        *,
        entity: str | None = None,
        metric: str | None = None,
        period: str | None = None,
        top_k: int = 10,
    ) -> FinEvidenceSearchResponse:
        payload = {
            "query": query,
            "filters": FinEvidenceFilters(entity=entity, metric=metric, period=period).model_dump(exclude_none=True),
            "top_k": top_k,
        }
        return self._request("/api/v1/evidence/search", FinEvidenceSearchResponse, payload)

    def coverage(self, question: str, required_claims: list[dict[str, Any]], evidence_ids: list[str]) -> FinEvidenceCoverageResponse:
        payload = {"question": question, "required_claims": required_claims, "evidence_ids": evidence_ids}
        return self._request("/api/v1/evidence/coverage", FinEvidenceCoverageResponse, payload)

    def table_query(self, *, entity: str | None = None, metric: str | None = None, period: str | None = None, top_k: int = 20) -> FinEvidenceTableResponse:
        payload = {key: value for key, value in {"entity": entity, "metric": metric, "period": period, "top_k": top_k}.items() if value is not None}
        return self._request("/api/v1/table/query", FinEvidenceTableResponse, payload)

    def verify(self, claim: str, evidence_ids: list[str]) -> FinEvidenceVerifyResponse:
        return self._request("/api/v1/evidence/verify", FinEvidenceVerifyResponse, {"claim": claim, "evidence_ids": evidence_ids})

    def citation(self, evidence_id: str) -> FinEvidenceCitation:
        path = f"/api/v1/evidence/{quote(evidence_id, safe='')}/citation"
        return self._request(path, FinEvidenceCitation)


class HttpEvidenceProvider:
    """Adapter from FinEvidence v1 evidence objects to runtime records."""

    name = "finevidence-http"
    qualification_authority = "external"

    def __init__(self, base_url: str | FinEvidenceClient, timeout_seconds: float = 10.0) -> None:
        self.client = base_url if isinstance(base_url, FinEvidenceClient) else FinEvidenceClient(base_url, timeout_seconds)

    def verify_claim(self, claim: str, evidence_ids: list[str]) -> bool:
        return self.client.verify(claim, evidence_ids).supported

    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]:
        query = " ".join([case.target, case.question, task.title, task.purpose, *(item.description for item in task.evidence_requirements)])
        evidence = self._retrieve(query, case, task)
        evidence_ids = [item.evidence_id for item in evidence]
        coverages: list[tuple[EvidenceRequirement, FinEvidenceCoverageResponse]] = []
        for requirement in task.evidence_requirements:
            coverages.append(
                (
                    requirement,
                    self.client.coverage(
                        query,
                        [self._requirement_payload(requirement, case.target)],
                        evidence_ids,
                    ),
                )
            )
        citations = {item.evidence_id: self.client.citation(item.evidence_id) for item in evidence}
        records: list[EvidenceRecord] = []
        for requirement, coverage in coverages:
            supported = {item.evidence_id: item for item in coverage.evidence}
            for item in evidence:
                citation = citations[item.evidence_id]
                if citation.evidence_id != item.evidence_id or citation.document_id != item.document_id:
                    raise EvidenceProviderError("citation does not match the searched evidence")
                records.append(self._record(item, citation, task, case, requirement, coverage.status, supported.get(item.evidence_id)))
        return records

    def _retrieve(self, query: str, case: ResearchCase, task: ResearchTask) -> list[FinEvidenceObject]:
        del case
        requirement = task.evidence_requirements[0] if len(task.evidence_requirements) == 1 else None
        return self.client.search(
            query,
            entity=requirement.entity if requirement else None,
            metric=requirement.metric if requirement else None,
            period=requirement.period if requirement else None,
            top_k=10,
        ).evidence

    @staticmethod
    def _requirement_payload(requirement: EvidenceRequirement, target: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "requirement_id": requirement.id,
            "description": requirement.description,
            "fact_type": requirement.fact_type,
            "role": requirement.role,
            "entity": requirement.entity or target,
            "criticality": requirement.criticality,
        }
        if requirement.evidence_role is not None:
            payload["evidence_role"] = requirement.evidence_role
        for field in ("metric", "period", "segment", "basis", "geography", "currency", "unit", "operation"):
            value = getattr(requirement, field)
            if value is not None:
                payload[field] = value
        return payload

    @staticmethod
    def _stance(requirement: EvidenceRequirement) -> Literal["SUPPORTING", "COUNTER", "CONFLICTING"]:
        stances = set(requirement.required_stances)
        if stances == {"COUNTER"}:
            return "COUNTER"
        if stances == {"CONFLICTING"}:
            return "CONFLICTING"
        return "SUPPORTING"

    @classmethod
    def _record(
        cls,
        item: FinEvidenceObject,
        citation: FinEvidenceCitation,
        task: ResearchTask,
        case: ResearchCase,
        requirement: EvidenceRequirement,
        coverage_status: str,
        coverage_item: FinEvidenceObject | None,
    ) -> EvidenceRecord:
        excerpt = item.content.text
        if not excerpt and item.content.table is not None:
            excerpt = json.dumps(item.content.table, sort_keys=True)
        if not excerpt and item.content.visual_reference is not None:
            excerpt = f"Visual evidence reference for {item.evidence_id}."
        if not excerpt:
            excerpt = f"Evidence object {item.evidence_id} has no textual payload."
        if len(excerpt) > 5000:
            marker = "\n[excerpt truncated; use the resolved citation for the complete source.]"
            excerpt = excerpt[: 5000 - len(marker)] + marker
        locator_parts = [f"page:{citation.page_number}"]
        for key, value in (("table", citation.table_id), ("row", citation.row_id), ("column", citation.column_id)):
            if value:
                locator_parts.append(f"{key}:{value}")
        verification = (coverage_item or item).verification
        content_hash = sha256(json.dumps({"evidence": item.model_dump(mode="json"), "citation": citation.model_dump(mode="json")}, sort_keys=True).encode("utf-8")).hexdigest()
        record_id = item.evidence_id if len(task.evidence_requirements) == 1 else f"{item.evidence_id}:{requirement.id}"
        qualified = coverage_status == "ELIGIBLE" and verification.coverage_status == "SUPPORTED"
        return EvidenceRecord(
            id=record_id,
            task_id=task.id,
            requirement_id=requirement.id,
            stance=cls._stance(requirement),
            qualification="QUALIFIED" if qualified else "NEEDS_REVIEW",
            source_id=citation.document_id,
            source_title=citation.document_name,
            excerpt=excerpt,
            provider=cls.name,
            source_url=citation.source_url,
            source_version=citation.document_hash or "finevidence-api-v1",
            locator=";".join(locator_parts),
            content_hash=content_hash,
            provenance={
                "case_id": case.id,
                "finevidence": {
                    "api_version": item.api_version,
                    "evidence_id": item.evidence_id,
                    "document_id": item.document_id,
                    "coverage_status": coverage_status,
                    "verification": verification.model_dump(mode="json"),
                    "citation": citation.model_dump(mode="json"),
                },
            },
        )


class HttpTableEvidenceProvider(HttpEvidenceProvider):
    """Exact metadata-first table evidence adapter for FinEvidence v1."""

    name = "finevidence-table-http"

    def _retrieve(self, query: str, case: ResearchCase, task: ResearchTask) -> list[FinEvidenceObject]:
        del query
        requirements = task.evidence_requirements
        entity = next((item.entity for item in requirements if item.entity), case.target)
        metric = next((item.metric for item in requirements if item.metric), None)
        period = next((item.period for item in requirements if item.period), None)
        return self.client.table_query(entity=entity, metric=metric, period=period, top_k=20).evidence


class DeterministicEvidenceProvider:
    """Local demo provider; it is not live market data or a substitute for FinEvidence."""

    name = "deterministic-demo"
    qualification_authority = "runtime"

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
