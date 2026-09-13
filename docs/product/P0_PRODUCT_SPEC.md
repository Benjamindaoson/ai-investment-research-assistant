# Financial DeepResearch Agent — P0 Product Specification

## Strategic positioning

The north-star product is an **AI Investment Analyst OS** for PE, VC, hedge
fund, and corporate-strategy teams. It automates the repetitive research work
around an investment question while keeping evidence, assumptions, uncertainty,
and human decision authority inspectable.

The first commercial workflow is not a general financial chatbot. It is:

```text
Investment Question
→ Research Plan
→ Autonomous Investigation
→ Evidence Map
→ Financial Analysis
→ Bull / Bear Debate
→ Investment Memo
→ Continuous Monitoring
```

Investment Memory is the long-term moat: previous theses, financial history,
risks, catalysts, open questions, and decision history should be available to a
later run. The repository owns the research/runtime and thesis/decision layer;
FinEvidence remains the independent evidence infrastructure. A future IC
workflow can add structured Bull, Bear, Financial, Industry, and Partner
reviews, but must remain evidence-linked and human-review-gated.

## Product boundary

Financial DeepResearch Agent is an evidence-first research operating system
for analysts. It turns a research question into a bounded plan, gathers and
qualifies evidence, records claims and counter-evidence, synthesizes a thesis,
and routes the result through human review before it becomes an investment
memo.

It is not a generic chatbot, a market-data terminal, a low-level RAG product,
an autonomous trading system, or a promise of investment performance.

## Product wedge by user

For an institutional research team, the product is a research execution and
control layer that can consume proprietary data and FinEvidence without
replacing Bloomberg, FactSet, Capital IQ, internal research systems, or the
firm's compliance controls. Its differentiator is the auditable chain from
research question to evidence-backed claim, counter-evidence, scenario thesis,
checkpoint, and human decision.

The first go-to-market user is an institutional investment or strategy team. An
individual investor can use the same evidence-first memo workflow later, but is
not the initial product wedge. In both cases, the product must reduce research
time while making source quality, uncertainty, disconfirming evidence, and
assumptions inspectable. A generic conversational stock assistant is not a
sufficient product wedge.

The first commercial proof point is an evidence-backed investment memo that a
user can reproduce and review later. Autonomous trade execution and broad
personal-finance features remain outside the product boundary.

## Canonical workflow

```text
Research Question
→ Research Task Contract
→ Dynamic Research DAG
→ Evidence Requirements
→ Research / Data / Computation
→ Evidence Qualification
→ Claims + Counter-Evidence
→ Thesis
→ Bull / Base / Bear
→ Risk / Catalyst
→ Human Review
→ Investment Memo
```

## P0 objects and invariants

- `ResearchCase` is the durable user-owned research question and scope.
- `ResearchPlan` records the planner identity, input hash, validation state, and
  evidence-bearing task DAG before execution.
- `ResearchRun` is an execution attempt with explicit state and timestamps; its
  mutable task state remains separate from the validated plan.
- `ResearchTask` is a typed unit in a dependency DAG; task completion is not
  inferred from model text.
- `EvidenceRequirement` states what must be observed before a claim qualifies.
- `EvidenceRecord` preserves source identity, excerpt, stance, verification
  status, and provenance. Supporting, counter, conflicting, and unverified
  evidence remain distinct.
- `Claim` links to evidence and has an explicit qualification state.
- `Thesis` records assumptions, disconfirming conditions, and bull/base/bear
  scenarios.
- `DecisionRecord` records analyst review and is the write authority for
  approval or rejection.
- `ToolExecution`, `Checkpoint`, and append-only events make execution
  auditable and recoverable.
- Planner quality is evaluated separately from execution quality; a plan must
  cover required research dimensions, dependencies, evidence requirements, and
  disconfirming conditions before it is compared with a future LLM planner.

The system must never silently fabricate sources, citations, financial facts,
tool results, or completed work. Unknown, partial, failed, cancelled, and
needs-review states are first-class outcomes.

## System boundary

The repository owns planning, task execution, financial analysis,
evidence consumption, synthesis, thesis and decision workflows, checkpoint /
recovery, trace, and evaluation.

FinEvidence is an independent Evidence Infrastructure. This repository owns a
typed provider boundary and evidence qualification, but does not reimplement a
document store, web crawler, multimodal RAG index, or source-ingestion system.
The planner is also a replaceable boundary: the current deterministic planner
is a local contract implementation, not an LLM claim.

## P0 experience

The Next.js workspace exposes one coherent analyst flow: Today → New Research →
Research Case → Evidence → Company Research → Thesis → Risk / Catalyst →
Monitor → Human Review → Living Brief → Versions → Library. The current UI is
an explicitly labelled synthetic-data prototype behind typed repository and
service contracts; it is not live market research.

## Out of scope for P0

GraphRAG, Neo4j, agent swarms, Kubernetes, complex permissions, broker or trade
execution, live portfolio actions, and a second RAG implementation are not part
of the canonical product line.
