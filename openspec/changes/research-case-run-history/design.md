## Context

Runs are persisted with an explicit `case_id` and opaque IDs. The store can
query that indexed column without adding a schema object.

## Goals / Non-Goals

**Goals:**

- Expose complete, typed run history for a known case.
- Preserve insertion order so latest history is deterministic locally.

**Non-Goals:**

- Pagination, filtering, or cross-tenant access control.
- A summary DTO that would discard run state.

## Decisions

Add a store query ordered by SQLite row insertion order, then validate each
payload through `ResearchRun` in the engine. The API first verifies the case so
an empty result cannot hide an unknown case.

## Risks / Trade-offs

- [Risk] A large case history will eventually need pagination → Mitigation:
  keep the endpoint response typed and add pagination before production-scale
  retention, without changing run identity.

## Migration Plan

No migration. Existing rows are immediately discoverable through the endpoint.
