## Why

Evidence qualification currently checks stance against the task requirement but
does not require a complete provenance tuple. That lets a record without a
source URL, locator, or content hash support a claim, undermining the product's
auditable and review-gated promise.

## What Changes

- Require `EvidenceRecord.provenance_complete` before assigning `QUALIFIED`.
- Keep incomplete records observable as `NEEDS_REVIEW` and preserve their
  provenance gaps in trace and memo state.
- Add a regression test using a stance-matching but incomplete record.

## Capabilities

### New Capabilities

- `evidence-qualification-integrity`: Provenance is a prerequisite for evidence
  qualification.

### Modified Capabilities

None.

## Impact

- One runtime qualification rule and its tests.
- No schema, persistence, provider, or frontend dependency changes.
