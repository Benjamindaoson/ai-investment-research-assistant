## Why

The runtime currently qualifies evidence through FinEvidence search,
requirement coverage, and citation resolution, but synthesized claims do not
consume the frozen claim verification endpoint. This leaves a gap between
evidence being retrievable and the claim actually being supported.

## What Changes

- Add an explicit claim verification capability to the FinEvidence adapter.
- Verify evidence-backed claims during synthesis when the external provider
  supports it.
- Demote unsupported claims to NEEDS_REVIEW.
- Mark the run PARTIAL when claim verification fails semantically.
- Mark the run FAILED with an auditable event when verification transport or
  contract errors prevent synthesis.

## Capabilities

### New Capabilities

- claim-verification-gate: Apply FinEvidence claim verification before a run
  can be considered complete.

### Modified Capabilities

## Impact

The evidence adapter, ResearchEngine synthesis state transition, and runtime
tests. The frozen FinEvidence API remains unchanged and no direct FinEvidence
imports are introduced.
