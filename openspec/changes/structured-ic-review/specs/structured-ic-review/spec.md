## ADDED Requirements

### Requirement: IC reviews are durable typed artifacts

The runtime SHALL persist an investment committee review with exactly one role
from `BULL`, `BEAR`, `FINANCIAL`, `INDUSTRY`, or `PARTNER`, an explicit
position, recommendation, reviewer, rationale, thesis ID, and evidence IDs.

#### Scenario: Valid role review is recorded

- **WHEN** a reviewer submits a valid role review for a run with a thesis
- **THEN** the runtime persists it on the run and emits an auditable review
  event

#### Scenario: Old runs remain readable

- **WHEN** a stored run has no IC review list
- **THEN** the runtime loads it with an empty list without changing existing
  red-team reviews or decisions

### Requirement: IC review evidence links are owned by the run

The runtime MUST reject an IC review when its thesis does not belong to the
run or any cited evidence ID is absent from the run. The runtime MUST preserve
each cited record's existing qualification state.

#### Scenario: Unknown evidence is rejected

- **WHEN** a review cites an evidence ID not present in the run
- **THEN** the API returns a validation error and does not append the review or
  event

#### Scenario: Unresolved evidence remains unresolved

- **WHEN** a valid review cites evidence with `NEEDS_REVIEW` or `UNQUALIFIED`
  qualification
- **THEN** the review is stored with the original evidence qualification intact

### Requirement: IC review records are readable and decision-linkable

The API SHALL expose append-only create/list operations for IC reviews and
SHALL allow a human decision to reference review IDs that belong to the same
run and thesis.

#### Scenario: Review list reads durable records

- **WHEN** a client requests IC reviews for an existing run
- **THEN** the API returns the persisted records in append order

#### Scenario: Decision references are validated

- **WHEN** a decision includes review IDs from another run or thesis
- **THEN** the API rejects the decision without changing the run or memory

### Requirement: The workspace makes panel coverage explicit

The runtime workspace SHALL display IC review records, role coverage, and
qualification-linked evidence references through typed query and mutation
boundaries. It MUST NOT display a missing role as a generated opinion.

#### Scenario: Missing roles are visible

- **WHEN** a run has reviews for only some panel roles
- **THEN** the workspace shows recorded roles and identifies the remaining
  roles as not yet reviewed

#### Scenario: Review mutation reads back server state

- **WHEN** a reviewer submits a valid IC review
- **THEN** the workspace invalidates or updates the run query and displays the
  server-returned review record
