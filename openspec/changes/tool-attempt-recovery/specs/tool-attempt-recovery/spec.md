## ADDED Requirements

### Requirement: Provider attempts are durable before execution
The runtime SHALL persist a uniquely identified tool attempt before invoking a provider, and SHALL update that attempt only after accepting the provider result or an explicit failure.

#### Scenario: Attempt starts durably
- **WHEN** a pending research task is about to call its provider
- **THEN** the run contains an `UNKNOWN_EFFECT` attempt with an `attempt_key` before provider work begins

#### Scenario: Successful attempt closes
- **WHEN** the provider returns and the current executor still owns the run
- **THEN** the same attempt becomes `SUCCEEDED` with a result hash and completion time

### Requirement: Unknown effects block automatic recovery
The runtime MUST NOT automatically retry an attempt whose outcome is unknown, and SHALL expose the run as blocked until an explicit resolution is recorded.

#### Scenario: Takeover blocks an unfinished attempt
- **WHEN** a new executor takes over a run with an unfinished provider attempt
- **THEN** the task becomes `UNKNOWN_EFFECT`, the run becomes `BLOCKED`, and no provider call is made

#### Scenario: Legacy running task is safe
- **WHEN** takeover finds a `RUNNING` task without an attempt record
- **THEN** the runtime creates a synthetic unknown attempt and blocks instead of guessing that retry is safe

### Requirement: Resolution is explicit and auditable
The runtime SHALL allow an authorized caller to resolve an unknown attempt by `RETRY` or `MARK_FAILED`, preserving the original attempt and recording the action.

#### Scenario: Explicit retry authorization
- **WHEN** the caller resolves a blocked unknown attempt with `RETRY`
- **THEN** only the matching task resets to `PENDING`, the run returns to `CREATED`, and a resolution event is recorded

#### Scenario: Explicit failure resolution
- **WHEN** the caller resolves a blocked unknown attempt with `MARK_FAILED`
- **THEN** the task and run become `FAILED`, the run receives a completion time, and no provider retry occurs

### Requirement: Unknown-effect state is visible in contracts
The backend and frontend contracts SHALL accept and render `UNKNOWN_EFFECT` tool attempts and `BLOCKED` runs without representing them as successful or completed research.

#### Scenario: Read-back preserves blocked state
- **WHEN** a blocked run is read through the API
- **THEN** its task and attempt states remain `UNKNOWN_EFFECT`, and the response does not contain a successful thesis generated after the unresolved attempt
