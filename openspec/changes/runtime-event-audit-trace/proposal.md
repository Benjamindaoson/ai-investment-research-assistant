## Why

The runtime already persists append-only events for state changes, leases, tool attempts, evidence, synthesis, and human review, but the live workspace does not expose that audit trail. Reviewers therefore cannot reconstruct what happened, in what order, or distinguish a durable state transition from the current projection.

## What Changes

- Add a typed read-only event transport for a research run.
- Render the run's append-only event history in chronological order with event type, timestamp, and compact payload details.
- Keep event payloads visible as structured JSON without allowing the frontend to mutate or reinterpret them.
- Add explicit loading, empty, transport-error, and populated states.

## Capabilities

### New Capabilities

- `runtime-event-audit-trace`: Read and inspect the durable event history for a research run.

### Modified Capabilities

## Impact

- Frontend runtime service, repository, query hook, and run workspace.
- No backend schema or persistence migration; the existing `GET /api/v1/research-runs/{run_id}/events` endpoint is the source of truth.
- No new dependency and no FinEvidence changes.
