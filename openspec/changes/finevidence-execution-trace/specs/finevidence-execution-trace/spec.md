## ADDED Requirements

### Requirement: Evidence execution receipts bind provider results to inputs

The runtime SHALL persist the selected evidence provider and a deterministic
SHA-256 input hash on every newly-created tool execution receipt.

#### Scenario: Successful provider execution is bound

- **WHEN** a research task invokes an evidence provider
- **THEN** its durable tool receipt contains the provider name and a 64-character
  input hash derived from the case and task contract

#### Scenario: Provider failure retains the binding

- **WHEN** the provider raises before returning evidence
- **THEN** the failed receipt still contains the same provider name and input
  hash used for that attempt

### Requirement: Evidence execution receipts summarize qualification

The runtime SHALL persist non-negative counts for returned evidence, qualified
evidence, review-needed evidence, and unqualified evidence after applying the
runtime qualification gate.

#### Scenario: Mixed evidence is summarized

- **WHEN** a provider returns records with different qualification outcomes
- **THEN** the succeeded receipt records counts whose sum equals the returned
  evidence count

#### Scenario: Empty evidence is summarized

- **WHEN** a provider returns no evidence records
- **THEN** the succeeded receipt records zero for every evidence count and keeps
  the deterministic empty-result hash

### Requirement: Execution metadata is backward compatible and bounded

The runtime SHALL accept receipts created before these fields existed and MUST
NOT persist raw provider queries, raw provider responses, or evidence excerpts
inside `ToolExecution`.

#### Scenario: Historical receipt loads

- **WHEN** a stored run contains a legacy tool receipt without execution
  metadata
- **THEN** the run loads with compatibility defaults and remains inspectable

#### Scenario: Trace exposes metadata without raw payloads

- **WHEN** the run API and frontend render an execution receipt
- **THEN** they expose provider, input hash, and bounded counts but no raw
  provider request or response body
