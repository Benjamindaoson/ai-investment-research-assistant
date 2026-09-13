## Why

The run-scoped financial analysis endpoint currently returns a valid,
evidence-linked calculation but does not retain it in the durable ResearchRun.
That makes the result disappear from the run projection and weakens recovery,
review, and auditability.

## What Changes

- Persist the latest evidence-linked financial analysis on the ResearchRun.
- Record a durable event when the analysis is written.
- Add a GET endpoint to read the persisted artifact.
- Expose the artifact through the typed frontend runtime service and workspace.
- Keep the explicit Decimal snapshot and qualified-evidence validation unchanged.

## Capabilities

### New Capabilities

- durable-financial-analysis-artifact: Persist and retrieve a run-scoped
  evidence-linked financial calculation.

### Modified Capabilities

## Impact

Affected domain models, SQLite run persistence, FastAPI routes, frontend
runtime transport, and the live run workspace. No new dependency and no
FinEvidence changes.
