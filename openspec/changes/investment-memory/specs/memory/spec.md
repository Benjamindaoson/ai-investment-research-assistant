## ADDED Requirements

### Requirement: Target memory retains versioned research references

The runtime SHALL persist a target-level memory projection containing ordered
case, run, memo, and thesis identifiers and the latest unresolved requirement
identifiers.

#### Scenario: First run for a target

- **WHEN** a run synthesizes a memo for a target with no prior memory
- **THEN** memory contains that run and thesis as the latest version and has no
  fabricated prior thesis reference

#### Scenario: Subsequent run for a target

- **WHEN** another run synthesizes a memo for the same target
- **THEN** memory retains both versions and exposes the prior latest thesis ID
  while pointing latest references at the new run

### Requirement: Memory is read-back durable and decision-aware

The runtime SHALL persist memory updates and append human decision references
without replacing the underlying run audit trail.

#### Scenario: Analyst decision recorded

- **WHEN** an analyst records a thesis decision
- **THEN** the target memory includes the decision ID and the run remains
  independently readable
