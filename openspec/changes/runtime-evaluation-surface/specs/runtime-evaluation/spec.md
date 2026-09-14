## ADDED Requirements

### Requirement: Reviewers can inspect run evaluation

The runtime workspace SHALL display the latest durable evaluation artifact,
including evaluator, overall pass state, and every check's status and detail.

#### Scenario: Evaluation exists

- **WHEN** the evaluation endpoint returns a valid artifact
- **THEN** the workspace displays its overall result and all check results

#### Scenario: Run has not been evaluated

- **WHEN** the evaluation endpoint returns its documented not-found response
- **THEN** the workspace shows an explicit not-evaluated state and does not
  claim success

#### Scenario: Evaluation retrieval fails

- **WHEN** the evaluation endpoint returns a transport or schema error
- **THEN** the workspace shows the error without hiding the current run

### Requirement: Evaluation remains read-only

The evaluation surface SHALL not alter run state, evidence, thesis, memo, or
decisions.

#### Scenario: Reviewer inspects checks

- **WHEN** the reviewer reads an evaluation check
- **THEN** the workspace presents the backend-provided status and detail
  without recomputing or promoting it
