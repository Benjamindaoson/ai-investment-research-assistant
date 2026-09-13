"""Framework-independent contracts persisted and replayed by the runtime."""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


RunState = Literal["CREATED", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED"]
TaskState = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]
EvidenceStance = Literal["SUPPORTING", "COUNTER", "CONFLICTING"]
EvidenceQualification = Literal["QUALIFIED", "NEEDS_REVIEW", "UNQUALIFIED"]


def default_required_stances() -> list[EvidenceStance]:
    return ["SUPPORTING"]


class ResearchCase(DomainModel):
    id: str = Field(min_length=1, max_length=120)
    question: str = Field(min_length=3, max_length=5000)
    target: str = Field(min_length=1, max_length=300)
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceRequirement(DomainModel):
    id: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)
    minimum_records: int = Field(default=1, ge=1, le=100)
    required_stances: list[EvidenceStance] = Field(default_factory=default_required_stances)


class ResearchTask(DomainModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    purpose: str = Field(min_length=3, max_length=2000)
    depends_on: list[str] = Field(default_factory=list)
    tool_name: str = Field(min_length=1, max_length=200)
    evidence_requirements: list[EvidenceRequirement] = Field(min_length=1)
    state: TaskState = "PENDING"


class ResearchPlan(DomainModel):
    id: str = Field(default_factory=lambda: f"plan-{uuid4().hex}")
    case_id: str = Field(min_length=1, max_length=120)
    question: str = Field(min_length=3, max_length=5000)
    planner_name: str = Field(min_length=1, max_length=200)
    planner_version: str = Field(min_length=1, max_length=100)
    input_hash: str = Field(min_length=64, max_length=64)
    status: Literal["PROPOSED", "VALIDATED", "REJECTED"] = "PROPOSED"
    tasks: list[ResearchTask] = Field(min_length=1)
    created_at: datetime = Field(default_factory=utc_now)


class ToolExecution(DomainModel):
    id: str = Field(default_factory=lambda: f"tool-{uuid4().hex}")
    task_id: str
    tool_name: str
    status: Literal["SUCCEEDED", "FAILED"]
    result_hash: str = Field(min_length=16, max_length=128)
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime = Field(default_factory=utc_now)


class EvidenceRecord(DomainModel):
    id: str = Field(default_factory=lambda: f"evidence-{uuid4().hex}")
    task_id: str
    requirement_id: str
    stance: EvidenceStance
    qualification: EvidenceQualification = "NEEDS_REVIEW"
    source_id: str = Field(min_length=1, max_length=300)
    source_title: str = Field(min_length=1, max_length=500)
    excerpt: str = Field(min_length=1, max_length=5000)
    provider: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_version: str | None = Field(default=None, max_length=200)
    locator: str | None = Field(default=None, max_length=500)
    content_hash: str | None = Field(default=None, min_length=16, max_length=128)
    retrieved_at: datetime = Field(default_factory=utc_now)
    provenance: dict[str, Any] = Field(default_factory=dict)

    @property
    def provenance_complete(self) -> bool:
        return bool(self.source_url and self.locator and self.content_hash)


class Claim(DomainModel):
    id: str = Field(default_factory=lambda: f"claim-{uuid4().hex}")
    task_id: str
    statement: str = Field(min_length=3, max_length=4000)
    evidence_ids: list[str] = Field(default_factory=list)
    status: Literal["DRAFT", "QUALIFIED", "NEEDS_REVIEW", "REJECTED"] = "DRAFT"
    confidence: float = Field(default=0.0, ge=0, le=1)


class Thesis(DomainModel):
    id: str = Field(default_factory=lambda: f"thesis-{uuid4().hex}")
    statement: str = Field(min_length=3, max_length=5000)
    bull: str = Field(min_length=1, max_length=3000)
    base: str = Field(min_length=1, max_length=3000)
    bear: str = Field(min_length=1, max_length=3000)
    claim_ids: list[str] = Field(default_factory=list)
    review_status: Literal["PENDING_REVIEW", "APPROVED", "NEEDS_REVIEW"] = "PENDING_REVIEW"


class DecisionRecord(DomainModel):
    id: str = Field(default_factory=lambda: f"decision-{uuid4().hex}")
    actor: str = Field(min_length=1, max_length=200)
    action: Literal["APPROVE_THESIS", "REJECT_THESIS", "REQUEST_RESEARCH"]
    target_id: str = Field(min_length=1, max_length=120)
    rationale: str = Field(min_length=3, max_length=4000)
    created_at: datetime = Field(default_factory=utc_now)


class Checkpoint(DomainModel):
    id: str = Field(default_factory=lambda: f"checkpoint-{uuid4().hex}")
    run_id: str
    state_version: int = Field(ge=1)
    completed_task_ids: list[str] = Field(default_factory=list)
    state_hash: str = Field(min_length=16, max_length=128)
    created_at: datetime = Field(default_factory=utc_now)


class ResearchRun(DomainModel):
    id: str = Field(min_length=1, max_length=120)
    case_id: str = Field(min_length=1, max_length=120)
    plan: ResearchPlan | None = None
    state: RunState = "CREATED"
    tasks: list[ResearchTask] = Field(min_length=1)
    tool_executions: list[ToolExecution] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    thesis: Thesis | None = None
    decisions: list[DecisionRecord] = Field(default_factory=list)
    checkpoint: Checkpoint | None = None
    state_version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None

    @model_validator(mode="after")
    def terminal_state_requires_completion_time(self) -> "ResearchRun":
        if self.state in {"COMPLETED", "PARTIAL", "FAILED", "CANCELLED"} and self.completed_at is None:
            raise ValueError("terminal runs require completed_at")
        return self


class EvaluationCheck(DomainModel):
    name: str
    status: Literal["PASS", "FAIL", "N/A", "BLOCKED"]
    detail: str


class EvaluationResult(DomainModel):
    case_id: str
    passed: bool | None
    checks: list[EvaluationCheck] = Field(min_length=1)
    evaluated_at: datetime = Field(default_factory=utc_now)
