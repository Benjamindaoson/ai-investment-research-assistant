## ADDED Requirements

### Requirement: Replanning can add typed research tasks

The runtime MUST merge new planner-provided task contracts into a partial run
when the planner declares dynamic task support, and MUST validate the complete
merged dependency DAG before persistence.

#### Scenario: New task is added and executed

- **WHEN** a partial run is replanned with a valid new task
- **THEN** the new task is persisted in the same run with PENDING state
- **AND** a later execute call runs the new task and checkpoints it

#### Scenario: Existing completed work is preserved

- **WHEN** a partial run is replanned with an additional task
- **THEN** completed independent tasks retain COMPLETED state and their evidence
- **AND** the original run ID remains unchanged

### Requirement: Invalid dynamic plans fail before mutation

The runtime MUST reject a replan whose merged task graph has duplicate IDs or
unknown dependencies without changing the persisted run.

#### Scenario: New task references an unknown dependency

- **WHEN** a replan returns a task depending on an unknown task ID
- **THEN** replanning fails with a validation error
- **AND** the prior run projection and events remain unchanged
