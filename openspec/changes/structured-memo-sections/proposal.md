## Why

The current `InvestmentMemo` is evidence-linked but structurally too thin for an
analyst or investment committee: it exposes one summary and flat ID lists, so
consumers cannot reliably render, evaluate, or export the memo's thesis, risks,
scenarios, and open questions. A stable section contract is the smallest step
from a runtime artifact to a reusable IC review artifact.

## What Changes

- Add a typed `MemoSection` contract with a stable key, review body, claim links,
  evidence links, and unresolved requirement links.
- Generate a deterministic, evidence-grounded section projection during memo
  synthesis; sections with insufficient support remain explicitly unresolved.
- Expose sections through the existing memo API and validate them at the web
  service boundary.
- Add section coverage tests and preserve the existing approval and no-fabrication
  semantics.

## Capabilities

### New Capabilities

- `structured-memo`: Stable, evidence-linked memo sections for review and export.

### Modified Capabilities

None. The existing memo behavior remains additive; the new capability defines
the structured projection.

## Impact

- Backend domain models and deterministic runtime synthesis.
- Existing memo JSON API; additive response field.
- Next.js runtime service schema and live run review surface.
- Backend and frontend tests; no new dependency or external provider.
