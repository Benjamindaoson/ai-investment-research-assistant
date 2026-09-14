## ADDED Requirements

### Requirement: Analysts can discover durable research cases

The runtime entry workspace SHALL display stored ResearchCases with target,
question, mandate decision type, and creation time when the runtime is
configured.

#### Scenario: Cases exist

- **WHEN** the case list returns one or more cases
- **THEN** the workspace displays each case's durable identity and metadata

#### Scenario: No cases exist

- **WHEN** the case list returns an empty list
- **THEN** the workspace shows an explicit empty state and keeps the new-case
  form available

#### Scenario: Case list fails

- **WHEN** the case list request fails
- **THEN** the workspace shows the error without hiding the new-case form

### Requirement: Analysts can reopen a case run

The case inbox SHALL link a case to its most recent durable run when at least
one run exists and SHALL not invent a run link when none exists.

#### Scenario: Case has a run

- **WHEN** case history contains one or more runs
- **THEN** the workspace provides a link to the most recent run workspace

#### Scenario: Case has no run

- **WHEN** case history is empty
- **THEN** the workspace labels the case as having no run yet
