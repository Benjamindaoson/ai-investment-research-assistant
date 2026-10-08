## Why

The runtime currently produces useful ratio calculations, but a financial
research memo cannot express how the thesis changes under explicit operating
assumptions or translate those assumptions into a reviewable valuation range.
Adding a small, deterministic scenario artifact now gives analysts a real
Bull/Base/Bear financial bridge while keeping every input explicit and
evidence-linked.

## What Changes

- Add a structured scenario analysis artifact with Bull, Base, and Bear cases.
- Require each scenario input to reference qualified evidence already present
  in the same research run.
- Calculate scenario revenue, operating income, free cash flow, and an
  illustrative terminal value using Decimal arithmetic only.
- Persist the artifact on the ResearchRun and expose it through the existing
  run API and typed frontend transport.
- Keep valuation illustrative and review-gated; do not infer missing inputs,
  fetch market prices, or place trades.

## Capabilities

### New Capabilities

- `structured-valuation-scenarios`: Evidence-linked Bull/Base/Bear operating
  scenarios and transparent valuation calculations.

### Modified Capabilities

## Impact

- Backend domain contracts, financial calculation service, run persistence, and
  API boundary.
- Frontend runtime schema and read-only financial artifact rendering.
- No new dependency, no FinEvidence changes, and no live market-data provider.
