## ADDED Requirements

### Requirement: Research task DAGs are validated before persistence

The runtime SHALL reject duplicate task IDs, unknown dependencies, dependency cycles, and tasks without evidence requirements before a case or run is written to durable storage.

#### Scenario: Valid DAG is accepted

- **WHEN** a plan contains unique tasks with known acyclic dependencies and evidence requirements
- **THEN** the engine persists the plan and creates a run with the same task contracts

#### Scenario: Invalid dependency is rejected

- **WHEN** a plan references a missing dependency or contains a cycle
- **THEN** the engine raises a validation error and durable storage contains no run for that request

### Requirement: Plan and execution state remain distinct

The runtime SHALL preserve the validated plan task contracts while allowing the run's task states to transition independently during execution and recovery.

#### Scenario: Execution mutates run state only

- **WHEN** a run executes one task and saves a checkpoint
- **THEN** the run task becomes completed while the persisted plan remains a validated record of the original task contract

#### Scenario: Resume uses the validated plan

- **WHEN** a run resumes after an interruption
- **THEN** the engine uses the persisted task dependencies and does not invent a different plan or duplicate completed task execution
