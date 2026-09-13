## ADDED Requirements

### Requirement: A run can resolve its target-level investment memory

The runtime SHALL expose the persisted `InvestmentMemory` associated with a
research run through a run-scoped read endpoint. The endpoint MUST resolve the
target from the persisted case and MUST NOT accept client-provided target data
for this lookup.

#### Scenario: Completed run has memory

- **WHEN** a completed run has synthesized a memo and target memory
- **THEN** the run-scoped endpoint returns the same memory payload as the
  target-scoped endpoint

#### Scenario: Unknown run

- **WHEN** a client requests memory for an unknown run
- **THEN** the endpoint returns HTTP 404 without creating memory

### Requirement: Live review surfaces observed memory deltas

The live runtime workspace SHALL show the current memory version and any
`ThesisDelta` only when the backend returns it. The UI MUST label the delta as
observed history and not as confidence, prediction, or investment advice.

#### Scenario: Prior thesis exists

- **WHEN** memory contains a previous thesis and latest ThesisDelta
- **THEN** the workspace displays the previous/current thesis IDs and the delta
  summary with its non-advice boundary

#### Scenario: First run has no prior thesis

- **WHEN** memory has no previous thesis or ThesisDelta
- **THEN** the workspace displays that this is the first recorded target run
