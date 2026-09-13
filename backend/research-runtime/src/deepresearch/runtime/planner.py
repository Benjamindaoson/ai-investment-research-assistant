"""Replaceable research planning boundary."""

from __future__ import annotations

from hashlib import sha256
from typing import Protocol

from deepresearch.domain.models import EvidenceRequirement, ResearchCase, ResearchPlan, ResearchTask


def research_input_hash(case: ResearchCase) -> str:
    return sha256(f"{case.id}|{case.target}|{case.question}".encode()).hexdigest()


class ResearchPlanner(Protocol):
    name: str
    version: str

    def plan(self, case: ResearchCase) -> ResearchPlan: ...


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
