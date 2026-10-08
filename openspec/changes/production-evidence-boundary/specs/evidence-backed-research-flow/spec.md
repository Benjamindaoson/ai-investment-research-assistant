## ADDED Requirements

### Requirement: Evidence-backed claims are traceable

The runtime SHALL only expose a qualified claim as evidence-backed when its evidence IDs resolve to persisted evidence records that satisfy the claim's task requirements. Unqualified or missing evidence SHALL produce a reviewable state.

#### Scenario: Qualified evidence produces a linked claim

- **WHEN** a task has the required qualified evidence and the runtime synthesizes its claim
- **THEN** the claim contains the persisted evidence IDs and the trace summary resolves those IDs to source provenance

#### Scenario: Missing evidence produces review state

- **WHEN** a task has no qualified evidence for a required requirement
- **THEN** the claim status is `NEEDS_REVIEW`, the run is not reported as fully completed, and the trace identifies the missing requirement

### Requirement: The end-to-end flow is deterministic without external credentials

The repository SHALL provide a deterministic provider path for tests that exercises qualification, synthesis, persistence, and recovery without network calls or credentials.

#### Scenario: Local deterministic run completes

- **WHEN** a test creates a case and executes its validated task DAG with the deterministic provider
- **THEN** the run persists events and a checkpoint, produces traceable claims, and can resume without duplicate completed tool executions

#### Scenario: Provider failure is not hidden as success

- **WHEN** evidence collection fails for a task
- **THEN** the runtime records the failure and leaves the task and run in an explicit unsuccessful or reviewable state
