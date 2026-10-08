## ADDED Requirements

### Requirement: Replanning is durable and requirement-driven

The runtime MUST support an explicit replan operation for a PARTIAL run. It
MUST preserve the run identity, prior evidence, and append-only event history,
and MUST record the unresolved requirements that triggered the replan.

#### Scenario: Partial run is replanned

- GIVEN a run is PARTIAL with unresolved requirements
- WHEN the analyst requests a replan
- THEN the planner receives the unresolved requirement IDs
- AND the validated plan is persisted
- AND the run becomes executable again

### Requirement: Replanning does not weaken terminal semantics

The runtime MUST reject replanning of COMPLETED, FAILED, or CANCELLED runs and
MUST leave those runs unchanged.

#### Scenario: Completed run is protected

- GIVEN a run is COMPLETED
- WHEN a replan is requested
- THEN the operation fails explicitly
- AND no new task execution or state mutation occurs

### Requirement: Retry evidence is idempotent

The runtime MUST NOT count an identical evidence record collected on a retry
more than once for a requirement.

#### Scenario: Provider repeats a record

- GIVEN a retry returns an evidence record already persisted for the same task
- WHEN the retry is merged
- THEN the record is not duplicated
- AND requirement qualification is based on distinct evidence IDs
