## ADDED Requirements

### Requirement: IC review traceability is evaluated

The deterministic run evaluator SHALL verify every IC review reference in the
Investment Memo and DecisionRecord against the current run and thesis. A
dangling or cross-thesis reference MUST fail the named evaluation check.

#### Scenario: Valid review references pass

- **WHEN** a memo or decision references IC reviews belonging to the evaluated
  run and thesis
- **THEN** the evaluator records an `ic_review_links` PASS check

#### Scenario: Dangling review reference fails

- **WHEN** a memo or decision references an IC review ID absent from the run
- **THEN** the evaluator records an `ic_review_links` FAIL check with the sorted
  dangling IDs

### Requirement: Golden cases may require review roles

The evaluator SHALL support an optional `required_ic_review_roles` golden-case
field. When present, every declared role MUST have at least one valid review;
when absent, no role-coverage check is required.

#### Scenario: Required roles are covered

- **WHEN** all roles declared by `required_ic_review_roles` have valid reviews
- **THEN** the evaluator records an `ic_review_coverage` PASS check

#### Scenario: Required role is missing

- **WHEN** one or more declared roles have no valid review
- **THEN** the evaluator records an `ic_review_coverage` FAIL check and does not
  claim the golden case passed
