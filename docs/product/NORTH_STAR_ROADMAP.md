# AI Investment Analyst OS — North-star roadmap

This roadmap separates the product promise from the verified implementation.
The runtime is the product core; agent labels are implementation details and do
not define the architecture.

## Killer workflow

1. An analyst submits a company or investment question.
2. The runtime creates a bounded, evidence-bearing research plan.
3. Research and computation tasks execute durably and can resume from a
   checkpoint.
4. Evidence is qualified, mapped to claims, and split into supporting, counter,
   conflicting, and unresolved states.
5. Financial analysis and scenario reasoning produce a reviewable thesis.
6. The system generates a living memo and records the human decision.
7. Later evidence can reopen assumptions and trigger monitoring work.

## Delivery sequence

### P0 — Research runtime foundation (implemented in this repository)

- Typed research case, plan, run, task, evidence, claim, thesis, decision,
  checkpoint, tool execution, evaluation, and memo contracts.
- Durable local SQLite state, append-only events, DAG execution, resume, trace,
  explicit provider/planner boundaries, and deterministic evaluation.
- Evidence-linked memo projection and a pure financial calculation boundary.
- Target-level Investment Memory that retains version references and unresolved
  requirements without copying chat transcripts.

### P1 — Production analyst workflow

- Connect a real FinEvidence deployment and validate source/version/locator
  read-back in integration tests.
- Replace the deterministic provider with registered research/data/computation
  tools while preserving the same task and evidence contracts.
- Add structured financial snapshots, scenario assumptions, and valuation
  outputs to memo sections with explicit provenance.
- Connect the Next.js workspace to runtime case/run/trace/memo APIs; retain a
  clearly labelled synthetic mode for local design work.

### P2 — Investment memory and review loop (beyond the current reference index)

- Persist company memory as versioned research artifacts, not an unbounded
  chat transcript.
- Compare new evidence against previous thesis assumptions and create a
  reviewable change record.
- Structured Bull/Bear/Industry/Financial/Partner review inputs are now
  available as append-only evidence-linked artifacts; richer consensus scoring
  remains out of scope.

### P3 — Monitoring and enterprise hardening

- Define monitor conditions over explicit assumptions, evidence requirements,
  and source updates.
- Add production storage, tenant isolation, identity, retention, and export
  controls only when the customer workflow requires them.

## Explicit non-goals

Do not build a second RAG system, an agent swarm, broker execution, or a large
dashboard before the single memo workflow is reliable. Success is measured by
research time saved, coverage of required evidence, memo quality, and analyst
hours saved—not by the number of agents or retrieval demos.
