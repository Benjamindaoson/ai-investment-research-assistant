## Why

The runtime already supports creating a new execution attempt for an existing
ResearchCase, preserving the case identity and its long-term memory. The live
workspace currently makes that capability inaccessible: analysts can inspect
history but cannot start the next controlled investigation from the case.

## What Changes

- Add a typed client and repository method for creating a run from an existing
  ResearchCase.
- Add a mutation that refreshes case history after creation and navigates to the
  newly created run.
- Add a clearly labelled rerun action to the case history surface with pending
  and error states.

## Capabilities

### New Capabilities

- `runtime-case-rerun`: Start a new durable runtime attempt for an existing
  ResearchCase.

### Modified Capabilities

- `runtime-case-history`: Add the analyst action that creates a new run from
  the current case.

## Impact

Affected frontend runtime service, repository, Query mutation, and history
component. Reuses the existing backend `POST /api/v1/research-cases/{case_id}/runs`
contract; no FinEvidence or database changes.
