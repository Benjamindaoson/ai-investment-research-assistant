## ADDED Requirements

### Requirement: External claims are verified before completion

When the configured evidence provider exposes claim verification, the runtime
MUST verify every synthesized claim that has qualified evidence before marking
the run COMPLETED.

#### Scenario: Provider supports the claim

- **WHEN** claim verification returns supported true
- **THEN** the claim remains QUALIFIED
- **AND** a run whose other requirements are qualified may become COMPLETED

#### Scenario: Provider does not support the claim

- **WHEN** claim verification returns supported false
- **THEN** the claim status becomes NEEDS_REVIEW
- **AND** the run state becomes PARTIAL rather than COMPLETED

### Requirement: Verification failures remain observable

The runtime MUST preserve provider transport or response-contract failures
that occur during claim verification as a FAILED run with an auditable event.

#### Scenario: Verification transport fails

- **WHEN** external claim verification cannot be completed
- **THEN** the run becomes FAILED
- **AND** the failure reason is recorded in a RUN_FAILED event
