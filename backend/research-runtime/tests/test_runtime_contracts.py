from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchRun, ResearchTask
from deepresearch.runtime.engine import validate_task_dag


def task(task_id: str, depends_on: list[str] | None = None) -> ResearchTask:
    return ResearchTask(
        id=task_id,
        title=task_id,
        purpose="Test a financial research question",
        depends_on=depends_on or [],
        tool_name="deterministic-research",
        evidence_requirements=[EvidenceRequirement(id=f"req-{task_id}", description="one source")],
    )


def test_terminal_run_requires_completion_time() -> None:
    with pytest.raises(ValidationError, match="terminal runs require completed_at"):
        ResearchRun(id="run-1", case_id="case-1", state="COMPLETED", tasks=[task("task")])


def test_task_dag_rejects_cycles() -> None:
    with pytest.raises(ValueError, match="cycle"):
        validate_task_dag([task("a", ["b"]), task("b", ["a"])])


def test_case_rejects_blank_question() -> None:
    with pytest.raises(ValidationError):
        ResearchCase(id="case-1", question=" ", target="ACME")


def test_evidence_requirement_defaults_and_validates_semantics() -> None:
    requirement = EvidenceRequirement(id="revenue", description="Revenue trend")

    assert requirement.fact_type == "RETRIEVED_FACT"
    assert requirement.role == "value"
    assert requirement.criticality == "CRITICAL"
    assert requirement.evidence_role is None

    with pytest.raises(ValidationError):
        EvidenceRequirement(id="revenue", description="Revenue trend", fact_type="UNKNOWN")
    with pytest.raises(ValidationError):
        EvidenceRequirement(id="revenue", description="Revenue trend", metric=" ")


def test_datetime_is_timezone_aware() -> None:
    run = ResearchRun(id="run-1", case_id="case-1", state="CREATED", tasks=[task("task")])
    assert run.created_at.tzinfo is not None
    assert datetime.now(UTC).tzinfo is not None
