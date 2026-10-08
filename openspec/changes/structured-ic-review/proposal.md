## Why

The runtime records a thesis, a generic red-team challenge, and a final human
decision, but it cannot preserve the distinct lenses an investment committee
uses to review a thesis. Without structured Bull, Bear, Financial, Industry,
and Partner inputs, review remains a text comment rather than an auditable
decision artifact.

## What Changes

- Add durable, evidence-linked IC review records with a fixed review role,
  position, recommendation, rationale, and reviewer identity.
- Support the five canonical lenses: Bull, Bear, Financial, Industry, and
  Partner.
- Validate cited evidence belongs to the run and preserve the existing
  evidence qualification boundary.
- Expose append-only create/list API endpoints and surface review records in the
  runtime workspace.
- Allow human decisions to reference the review records they considered,
  without breaking older decisions that predate the panel artifact.

## Capabilities

### New Capabilities

- `structured-ic-review`: Durable role-based investment committee reviews that
  remain linked to the thesis, run, evidence, and human decision.

### Modified Capabilities

## Impact

- Backend domain models, runtime engine, API, persistence serialization, and
  tests.
- Frontend runtime service, repository, query hooks, review form, and run
  workspace.
- No new dependency, no FinEvidence changes, and no automatic investment
  recommendation.
