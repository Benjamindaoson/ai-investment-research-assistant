## Why

The runtime persists ResearchCases and exposes run history, but the `/runtime`
entry currently only creates a new case. Analysts cannot discover or reopen
their durable research cases after leaving a run page.

## What Changes

- Add a read-only `GET /api/v1/research-cases` runtime endpoint.
- Add typed frontend case-list transport and query state.
- Render existing cases with target, question, mandate, and a link to the most
  recent run while preserving the create-case form.

## Capabilities

### New Capabilities

- `runtime-case-inbox`: Discover and reopen durable ResearchCases.

### Modified Capabilities

- None.

## Impact

Small backend persistence/API addition and frontend service/repository/query/
entry-page changes. No change to run execution, FinEvidence, or schemas of
existing endpoints.
