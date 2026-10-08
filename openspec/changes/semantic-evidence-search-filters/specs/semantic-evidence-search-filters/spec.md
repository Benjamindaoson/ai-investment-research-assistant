## ADDED Requirements

### Requirement: Explicit financial search slots reach FinEvidence

The HTTP client MUST serialize explicit entity, metric, and period slots into
the frozen FinEvidence search `filters` object.

#### Scenario: Single requirement uses typed search filters

- **WHEN** a task has one requirement with entity, metric, and period
- **THEN** the search request contains those exact filter values
- **AND** the coverage request preserves the same requirement contract.

#### Scenario: Missing slots are not fabricated

- **WHEN** an explicit requirement omits metric or period
- **THEN** those keys are absent from the search filters.

### Requirement: Ambiguous multi-requirement searches remain safe

The provider MUST NOT combine incompatible slots from multiple requirements
into one search filter tuple.

#### Scenario: Multiple requirements use broad search

- **WHEN** a task has more than one evidence requirement
- **THEN** the provider performs a broad search and lets coverage qualify each
  requirement independently.
