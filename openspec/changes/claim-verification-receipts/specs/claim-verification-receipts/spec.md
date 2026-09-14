## ADDED Requirements

### Requirement: Claim verification creates a durable attempt receipt

When a provider exposes claim verification, the runtime SHALL persist an
`UNKNOWN_EFFECT` verification receipt before invoking it, including the run,
claim/task, provider, operation, attempt key, and deterministic input hash.

#### Scenario: Verification attempt is visible before the call

- **WHEN** a provider's `verify_claim` method is about to be invoked
- **THEN** the persisted run contains an in-flight verification receipt before
  the method is called

#### Scenario: Verification input is bound

- **WHEN** a claim is verified against evidence IDs
- **THEN** the receipt input hash is a 64-character deterministic hash of the
  claim statement and evidence IDs

### Requirement: Verification outcomes remain explicit

The runtime SHALL mark a completed verification call `SUCCEEDED` and persist
whether the provider supported the claim. A `supported=false` response MUST
remain a successful negative observation and SHALL move the claim to
`NEEDS_REVIEW`; provider failures SHALL remain `FAILED`.

#### Scenario: Provider supports a claim

- **WHEN** verification returns `supported=true`
- **THEN** the receipt is `SUCCEEDED` with `verification_supported=true` and
  the claim remains eligible for completion

#### Scenario: Provider rejects a claim

- **WHEN** verification returns `supported=false`
- **THEN** the receipt is `SUCCEEDED` with `verification_supported=false` and
  the claim is `NEEDS_REVIEW`

#### Scenario: Verification transport fails

- **WHEN** verification raises a provider error
- **THEN** the receipt is `FAILED` with bounded diagnostic fields and the run
  is `FAILED`

### Requirement: Verification obeys lease-loss recovery semantics

Verification receipt writes SHALL use the current run lease, and a lease loss
before result adoption MUST leave the persisted attempt unresolved rather than
publishing a stale success or failure.

#### Scenario: Lease is lost during verification

- **WHEN** the heartbeat loses ownership while `verify_claim` is in flight
- **THEN** the executor raises lease loss and does not persist the verification
  result as current run state

### Requirement: Verification receipts are exposed without raw payloads

The run API and frontend tool trace SHALL expose the operation and supported
result while MUST NOT expose raw claim-provider request or response bodies.

#### Scenario: Analyst inspects verification trace

- **WHEN** a run contains a completed verification receipt
- **THEN** the trace identifies it as claim verification and shows its supported
  result and hashes
