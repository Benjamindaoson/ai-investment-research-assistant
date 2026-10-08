## ADDED Requirements

### Requirement: Table evidence is a registered FinEvidence data tool

The runtime SHALL provide an HTTP-backed `financial-table` tool that calls only
FinEvidence v1 `/api/v1/table/query`, converts returned objects through the
existing coverage/citation/provenance path, and returns `EvidenceRecord` values.

#### Scenario: Table task uses exact slots

- **WHEN** a task declares a requirement with entity, metric, and period slots
  and resolves to `financial-table`
- **THEN** the provider sends those slots to `/api/v1/table/query` and the
  resulting records retain the existing external qualification boundary

#### Scenario: Table result preserves citation identity

- **WHEN** the table endpoint returns evidence and citation resolution succeeds
- **THEN** every returned record links the same evidence ID and document ID to
  its citation, source locator, URL, and content hash

### Requirement: Existing search and deterministic paths remain stable

The runtime SHALL keep existing search-provider behavior and SHALL register
`financial-table` automatically only for a configured real FinEvidence HTTP
provider; deterministic defaults and explicit registries MUST NOT gain a hidden
network dependency.

#### Scenario: Existing search task is unchanged

- **WHEN** an existing task resolves to `external-evidence`
- **THEN** it continues to use `/api/v1/evidence/search` and the same evidence
  qualification behavior

#### Scenario: Explicit registry remains authoritative

- **WHEN** an application supplies a custom `ResearchToolRegistry`
- **THEN** the factory does not silently add or replace tools

### Requirement: Missing table evidence remains honest

The table provider MUST preserve empty, partial, unsupported, and transport
failure outcomes without inventing financial values or promoting evidence to
qualified outside the existing provider authority.

#### Scenario: No table evidence is found

- **WHEN** `/api/v1/table/query` returns an empty evidence list
- **THEN** the task receives no fabricated records and downstream coverage can
  remain unresolved
