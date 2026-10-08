## Why

The runtime intentionally supports deterministic fixtures for local development, but the workspace currently does not expose whether a run is backed by FinEvidence or synthetic evidence. Analysts need this boundary visible before interpreting any output.

## What Changes

- Extend the existing runtime health response with evidence, planner, synthesizer, and registered-tool identities.
- Add a typed frontend health read and render a compact readiness panel on the live run page.
- Label deterministic mode as a fixture and live mode as external evidence; do not change provider selection or add fallback behavior.

## Capabilities

### New Capabilities

- `runtime-provider-readiness`: Expose and display the configured runtime capability boundary.

### Modified Capabilities

## Impact

- Backend health response, frontend service/repository/query, and live runtime workspace.
- No persistence, domain model, FinEvidence, or dependency changes.
