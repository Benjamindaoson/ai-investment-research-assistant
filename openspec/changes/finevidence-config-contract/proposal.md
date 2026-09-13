## Why

The frozen FinEvidence handoff specifies `FIN_EVIDENCE_BASE_URL`, while the
runtime currently reads the legacy spelling `FINEVIDENCE_BASE_URL`. Starting the
system exactly as documented therefore selects the local deterministic provider
without making the configuration mistake visible.

## What Changes

- Make `FIN_EVIDENCE_BASE_URL` the canonical runtime configuration.
- Make `FIN_EVIDENCE_TIMEOUT_SECONDS` the canonical timeout configuration.
- Keep the existing `FINEVIDENCE_*` names as explicitly documented compatibility
  aliases.
- Add configuration-selection tests and update runbooks.

## Capabilities

### New Capabilities

- `finevidence-config-contract`: Select the external evidence provider from the
  frozen integration configuration.

### Modified Capabilities

## Impact

Runtime app configuration, backend tests, and documentation. No FinEvidence
code or wire contract changes.
