## ADDED Requirements

### Requirement: Qualified evidence must be auditable

The runtime SHALL assign `QUALIFIED` only when an evidence record both matches a
task's required stance and has complete provenance. Complete provenance MUST
include source URL, locator, and content hash.

#### Scenario: Complete supporting evidence

- **WHEN** a supporting record matches a supporting requirement and has complete
  provenance
- **THEN** the runtime marks it `QUALIFIED` and allows it to support a claim

#### Scenario: Incomplete matching evidence

- **WHEN** a record matches the required stance but lacks any provenance field
- **THEN** the runtime marks it `NEEDS_REVIEW`, excludes it from qualified claim
  support, and keeps it in the run trace

### Requirement: Provenance failure remains visible

The runtime SHALL preserve incomplete evidence in the run and expose its effect
through evidence qualification counts and unresolved requirements.

#### Scenario: Incomplete evidence prevents completion

- **WHEN** incomplete evidence is the only record for a required evidence
  requirement
- **THEN** the run is `PARTIAL` and the memo exposes the unresolved requirement
