## ADDED Requirements

### Requirement: Analysts can record an explicit thesis decision

The runtime workspace MUST allow an analyst to submit an approve, reject, or
request-research decision for the current synthesized thesis with an explicit
actor and rationale.

#### Scenario: Submit an approval decision

- **WHEN** an analyst submits APPROVE_THESIS for a completed run with a thesis
- **THEN** the client POSTs the run ID, thesis ID, actor, action, and rationale
- **AND** the workspace displays the backend-updated thesis and memo status

#### Scenario: Backend rejects an ineligible approval

- **WHEN** an analyst attempts to approve a thesis for a non-completed run
- **THEN** the backend rejection is surfaced as an error
- **AND** the workspace does not replace the cached run with a fabricated success

### Requirement: Decision history is auditable and read-only

The runtime workspace MUST display recorded decisions from the run response with
their actor, action, target, rationale, and timestamp, without edit or delete
controls.

#### Scenario: Display prior decisions

- **WHEN** a run response contains one or more decisions
- **THEN** the workspace renders each decision's actor, action, rationale, and
  timestamp
- **AND** the decision list is read-only

#### Scenario: Older run response omits decisions

- **WHEN** a compatible backend response has no decisions field
- **THEN** the typed client treats decisions as an empty list
