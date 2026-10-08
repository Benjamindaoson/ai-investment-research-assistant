## Why

The runtime currently accepts only a target and a question. Without an explicit
decision mandate, the planner cannot distinguish a screening question from an
investment-committee memo, a short-term catalyst review from a long-horizon
thesis, or a high-materiality decision from exploratory research.

## What Changes

- Add a validated ResearchMandate contract to ResearchCase and ResearchPlan.
- Capture decision type, time horizon, materiality, required outputs, and constraints.
- Include the mandate in planner input hashing and planner provenance.
- Extend the runtime create-case API and typed frontend service.
- Add mandate fields to the canonical runtime start workspace.
- Preserve defaults so existing stored cases and older clients remain readable.

## Capabilities

### New Capabilities

- research-mandate: Capture and preserve explicit decision scope before planning.

### Modified Capabilities

## Impact

Backend domain models, planner hashing/provenance, create-case API, backend tests,
frontend runtime service, runtime start workspace, and frontend tests. No
FinEvidence changes and no new retrieval implementation.
