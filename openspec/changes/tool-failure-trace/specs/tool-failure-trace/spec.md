## ADDED Requirements

### Requirement: Provider failures produce auditable tool traces
The runtime SHALL append a `ToolExecution` record with `FAILED` status when a provider call raises, and SHALL preserve the associated task and run failure as distinct from successful empty evidence.

#### Scenario: Provider exception is traced
- **WHEN** a provider raises while collecting evidence for a running task
- **THEN** the persisted run contains a failed tool execution for that task and the run transitions to `FAILED`

#### Scenario: Empty evidence remains successful
- **WHEN** a provider returns an empty evidence list without raising
- **THEN** the tool execution is `SUCCEEDED` with the deterministic empty-result hash and the runtime does not classify it as a provider failure

### Requirement: Failure diagnostics are bounded and typed
A failed tool execution SHALL include the exception type, a bounded diagnostic message, and a deterministic hash of the full diagnostic input; it MUST NOT require persisting a raw provider response.

#### Scenario: Diagnostic fields are recorded
- **WHEN** a provider raises an exception with a message
- **THEN** the failed execution includes its exception type, at most 1000 characters of message, and a SHA-256 diagnostic hash

#### Scenario: Existing successful traces remain valid
- **WHEN** a persisted successful tool execution has no failure diagnostic fields
- **THEN** the domain and frontend contracts accept it unchanged

### Requirement: Failure traces obey execution ownership
Failure trace writes during leased execution SHALL use the same current-lease guard as other run state writes and SHALL NOT allow a stale executor to publish a failure for a newer owner.

#### Scenario: Stale failure is rejected
- **WHEN** lease ownership is lost before a provider exception can be persisted
- **THEN** the stale executor raises lease loss and does not publish its failure trace as current run state
