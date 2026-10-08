## ADDED Requirements

### Requirement: Run review exposes tool execution receipts

The runtime workspace MUST display each returned tool execution as a read-only
record with tool name, task ID, status, result hash, and timestamps when present.

#### Scenario: Display a successful execution

- **WHEN** a run response contains a successful tool execution
- **THEN** the workspace displays its tool name, task ID, success status, result
  hash, and start/completion timestamps

#### Scenario: Display a failed execution

- **WHEN** a run response contains a failed tool execution
- **THEN** the workspace preserves and visibly displays the failed status
- **AND** it does not infer task success from the existence of the record

#### Scenario: Historical run without executions

- **WHEN** a compatible run response omits tool executions
- **THEN** the workspace continues to render
- **AND** it displays an explicit empty-state message
