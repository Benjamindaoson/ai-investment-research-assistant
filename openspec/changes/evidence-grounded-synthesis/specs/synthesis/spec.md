## ADDED Requirements

### Requirement: Claims are derived from qualified evidence

The runtime SHALL create each claim from evidence belonging to the claim's task,
link only qualified evidence IDs, and never use a fixed confidence value.

#### Scenario: Task has qualified and unresolved evidence

- **WHEN** a task produces evidence with multiple stances and qualifications
- **THEN** its claim reports observed counts, links only qualified records, and
  confidence equals qualified records divided by observed records

#### Scenario: Task has no qualified evidence

- **WHEN** a task has no evidence satisfying its requirements
- **THEN** its claim is `NEEDS_REVIEW`, has no evidence links, and has zero
  confidence

### Requirement: Thesis scenarios remain review-gated and auditable

The runtime SHALL derive Bull/Base/Bear text from observed task and evidence
state, and SHALL mark the thesis as needing review when any requirement is not
satisfied.

#### Scenario: All task requirements qualify

- **WHEN** every task satisfies its evidence requirements
- **THEN** the thesis is `PENDING_REVIEW` and its scenarios identify observed
  evidence state without asserting unobserved financial facts

#### Scenario: A requirement remains unresolved

- **WHEN** at least one task does not satisfy its evidence requirements
- **THEN** the thesis is `NEEDS_REVIEW` and the unresolved state is visible in
  the scenario text
