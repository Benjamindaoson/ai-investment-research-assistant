## Why

The FinEvidence client has strong mocked contract tests, but the product's
real boundary is not proven until a configured runtime can read actual
evidence, resolve citations, and preserve partial coverage honestly. The local
catalog is available, so this needs an explicit opt-in smoke rather than an
always-on test that depends on external service state.

## What Changes

- Add an opt-in integration test for the frozen FinEvidence v1 HTTP boundary.
- Exercise health, search, coverage, citation resolution, and runtime record
  conversion through `HttpEvidenceProvider`.
- Validate identity/provenance invariants without requiring a particular
  investment claim to be covered.
- Report empty/partial target coverage as an observed result, not a failure of
  the runtime contract.

## Capabilities

### New Capabilities

- `finevidence-integration-smoke`: Explicitly runs a real HTTP evidence-chain
  smoke against a configured FinEvidence deployment.

### Modified Capabilities

## Impact

- New opt-in backend integration test and pytest marker configuration.
- Runtime documentation with the command and honest interpretation of results.
- No FinEvidence source changes, no direct internal imports, and no default
  network dependency for the unit-test suite.
