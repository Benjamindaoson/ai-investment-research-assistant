## Why

The runtime can now persist evidence-linked valuation scenarios through HTTP,
but an analyst still has to construct the payload outside the product. That
breaks the primary workflow and makes the new artifact effectively API-only.
The runtime workspace should provide a compact, explicit input surface that
cannot submit without qualified evidence.

## What Changes

- Add a frontend form for base revenue and Bull/Base/Bear assumptions.
- Require one qualified evidence selection for each scenario before submit;
  the UI expands that selection into the backend's field-level link map.
- Add typed POST transport and a TanStack Query mutation for the artifact.
- Render loading, validation, error, success, and refreshed read-only output
  states without fabricating values.

## Capabilities

### New Capabilities

- `valuation-scenario-input-workflow`: Analyst entry and submission of
  evidence-linked scenario valuation assumptions.

### Modified Capabilities

## Impact

- Frontend runtime service, repository, query hook, workspace, and tests.
- No backend contract change, no new dependency, and no FinEvidence change.
