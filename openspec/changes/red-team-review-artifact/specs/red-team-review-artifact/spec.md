## ADDED Requirements

### Requirement: Red-team reviews are durable and thesis-scoped

The runtime MUST append a RedTeamReview to the current thesis's ResearchRun
and preserve reviewer, challenge, cited evidence, outcome, and rationale.

#### Scenario: Record a red-team challenge

- **WHEN** an analyst records a valid challenge for a run with a thesis
- **THEN** the review is returned with a stable ID
- **AND** a subsequent run read includes the review

### Requirement: Red-team evidence links are bounded

Every cited red-team evidence ID MUST exist in the same run and have COUNTER
or CONFLICTING stance.

#### Scenario: Dangling or supporting evidence is cited

- **WHEN** a review cites an unknown or supporting-only evidence ID
- **THEN** the request fails with a validation error
- **AND** the ResearchRun is not mutated

### Requirement: Red-team outcomes affect review readiness explicitly

An outcome of REQUIRES_RESEARCH MUST set the thesis review status to
NEEDS_REVIEW and MUST append an auditable event.

#### Scenario: Challenge requires more research

- **WHEN** a valid review is recorded with REQUIRES_RESEARCH
- **THEN** the thesis review status becomes NEEDS_REVIEW
- **AND** RED_TEAM_REVIEW_RECORDED identifies the outcome and evidence IDs
