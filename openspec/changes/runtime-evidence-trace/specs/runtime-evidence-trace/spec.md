## ADDED Requirements

### Requirement: Runtime evidence remains inspectable

The runtime workspace MUST display each returned evidence record's stance,
qualification, source identity, excerpt, and available provenance metadata.

#### Scenario: Inspect qualified supporting evidence

- **WHEN** a run contains a qualified supporting EvidenceRecord
- **THEN** the workspace displays its source title, excerpt, stance, and
  qualification
- **AND** it displays locator and content hash when returned

#### Scenario: Inspect counter or conflicting evidence

- **WHEN** a run contains counter or conflicting evidence
- **THEN** the workspace keeps its stance visibly distinct from supporting
  evidence
- **AND** the record remains visible even when its qualification is
  NEEDS_REVIEW or UNQUALIFIED

### Requirement: Missing provenance is explicit

The runtime workspace MUST NOT fabricate citations or provenance when the
backend omits them.

#### Scenario: Incomplete provenance

- **WHEN** an evidence record lacks a source URL, locator, or content hash
- **THEN** the workspace labels provenance as incomplete or unavailable
- **AND** it does not render a fabricated source link or hash

#### Scenario: Historical minimal response

- **WHEN** a compatible backend response contains only the minimal evidence
  fields
- **THEN** the typed client accepts the response
- **AND** unavailable detail fields remain visibly unavailable
