## Context

The store already keys runs, events, and checkpoints by `run_id`, while
`ResearchCase` is persisted separately. The current ID convention conflates the
parent case and an execution attempt.

## Goals / Non-Goals

**Goals:**

- Give each run a collision-resistant opaque ID.
- Keep `case_id` as the canonical parent relationship.
- Preserve resume and read-back behavior.

**Non-Goals:**

- Listing runs by case (a separate query/API slice).
- Changing historical IDs or migrating existing databases.

## Decisions

Use the existing `uuid4` dependency already used by domain IDs and generate
`run-{uuid4().hex}` at creation. Do not derive identity from mutable question or
case data; the case relationship remains explicit in `ResearchRun.case_id`.

## Risks / Trade-offs

- [Risk] Clients that inferred a run ID from a case ID break → Mitigation: API
  clients already receive `run_id` from case creation and should treat it as
  opaque; the old accidental convention was never a declared contract.
- [Risk] Existing rows retain the old format → Mitigation: reads remain
  format-agnostic and no migration rewrites durable history.

## Migration Plan

Deploy the creation change. Existing runs are readable; new runs receive unique
IDs. No destructive migration is needed.
