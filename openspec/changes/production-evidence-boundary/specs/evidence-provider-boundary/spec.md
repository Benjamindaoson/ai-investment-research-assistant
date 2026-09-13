## ADDED Requirements

### Requirement: Evidence records preserve external provenance

The runtime SHALL represent externally supplied evidence with a stable source identity, optional source version, source URL, locator, content hash, provider identity, and retrieval timestamp. Fixture evidence MUST be explicitly identifiable as non-production data.

#### Scenario: Complete external evidence is accepted

- **WHEN** a provider returns an evidence record with source identity, URL, locator, content hash, provider, retrieval time, and provenance
- **THEN** the runtime accepts the record and preserves every provenance field in the persisted run

#### Scenario: Missing external provenance is reviewable

- **WHEN** a provider returns an evidence record without a source URL, locator, or content hash
- **THEN** the runtime does not claim the record is fully production-qualified and exposes the missing provenance in the trace summary

### Requirement: Provider payloads are versioned and validated

The HTTP provider adapter SHALL accept only a supported schema version and SHALL reject malformed records, unknown top-level payload shapes, and invalid evidence references before they enter the runtime.

#### Scenario: Unsupported provider schema is rejected

- **WHEN** the provider response declares an unsupported schema version
- **THEN** the adapter raises an explicit provider contract error and the research task is not marked completed

#### Scenario: Malformed record is rejected

- **WHEN** the provider response contains an evidence record that fails the domain contract
- **THEN** the adapter rejects the response with validation context and does not fabricate a replacement record

### Requirement: Provider transport failures remain observable

The runtime SHALL preserve provider timeout, connection, and non-success HTTP failures as explicit failures with provider context.

#### Scenario: Provider times out

- **WHEN** the configured evidence provider exceeds its bounded timeout
- **THEN** the task remains unsuccessful, the run records a failure event, and no successful tool execution is written for that task

#### Scenario: Provider returns a non-success response

- **WHEN** the provider responds with a non-2xx status
- **THEN** the adapter raises an explicit provider error containing the status and the runtime does not mark the task completed
