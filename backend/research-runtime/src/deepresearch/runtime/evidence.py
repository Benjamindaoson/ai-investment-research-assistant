"""Evidence consumption boundary owned by FinEvidence in production."""

from hashlib import sha256
from typing import Protocol

from deepresearch.domain.models import EvidenceRecord, ResearchCase, ResearchTask


class EvidenceProvider(Protocol):
    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]: ...


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
                        provenance={"fixture": True, "case_id": case.id},
                    ),
                ]
            )
        return records


def evidence_hash(evidence: list[EvidenceRecord]) -> str:
    material = "|".join(f"{item.id}:{item.qualification}:{item.stance}" for item in evidence)
    return sha256(material.encode()).hexdigest()
