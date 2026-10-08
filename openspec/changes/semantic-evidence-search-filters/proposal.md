## Why

The Runtime already declares structured evidence semantics, but its HTTP search
adapter only embeds those values in free-text. Exact entity/metric/period
retrieval therefore cannot use the frozen FinEvidence filter contract.

## What Changes

- Extend the typed FinEvidence client search method with metric and period
  filters.
- Forward explicit slots from a single task requirement to search.
- Leave multi-requirement tasks unfiltered rather than merging incompatible
  slots, while retaining full coverage payload semantics.

## Capabilities

### New Capabilities

- `semantic-evidence-search-filters`: Explicit requirement slots reach the
  external evidence search boundary.

### Modified Capabilities

## Impact

- Runtime FinEvidence client/provider and unit/integration tests.
- No FinEvidence source changes, no new dependency, and no fallback behavior.
