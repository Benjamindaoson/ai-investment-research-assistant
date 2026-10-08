## Context

Financial analysis already accepts explicit Decimal values and requires every
supplied field to link to QUALIFIED evidence in the same run. The calculation
is currently returned synchronously but is not part of the persisted run
projection.

## Goals / Non-Goals

**Goals:**

- Make one run-scoped financial analysis durable and readable after restart.
- Preserve the exact field-to-evidence mapping and calculation output.
- Emit an append-only event for audit and recovery diagnostics.
- Surface the artifact without bypassing the frontend service/repository boundary.

**Non-Goals:**

- Multiple historical financial-analysis versions in one run.
- Automatic table parsing, valuation, market-data retrieval, or FinEvidence
  changes.

## Decisions

Store the latest result, including the explicit input snapshot, as an optional
financial_analysis field on ResearchRun.
This is the smallest durable shape compatible with the current single-snapshot
endpoint; a future version can introduce versioned artifacts when the product
has a real multi-period workflow.

Add ResearchEngine.record_financial_analysis as the write authority. The
method reuses the same run/evidence qualification checks as the POST route,
updates the run, persists it, and appends FINANCIAL_ANALYSIS_RECORDED. The API
delegates to this method and the GET route reads from the run.

Extend the existing runtime Zod schema, repository, and workspace. The
workspace renders the artifact only when present and labels its evidence-link
count; it does not invent an input form or synthetic financial values.

## Risks / Trade-offs

- [Only latest result retained] → The endpoint is currently single-snapshot;
  introduce versioned analysis records when a concrete multi-period UX exists.
- [Existing persisted runs lack the new field] → Use an optional field with a
  null default so existing SQLite payloads remain readable.

## Migration Plan

Deploy the additive model and route change. Existing runs deserialize with a
null analysis. Rollback is safe at the code level because the persisted field
is additive; clients can continue using the existing POST endpoint.
