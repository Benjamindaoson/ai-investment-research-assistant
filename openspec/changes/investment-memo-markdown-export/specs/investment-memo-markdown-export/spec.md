## ADDED Requirements

### Requirement: Analysts can export the current investment memo

The runtime workspace SHALL offer a Markdown download when a durable memo is
present.

#### Scenario: Memo exists

- **WHEN** the run contains a memo and the analyst activates the export action
- **THEN** the browser downloads a Markdown projection containing the run,
  memo status, thesis, structured sections, evidence IDs, and unresolved
  requirements

#### Scenario: Memo is absent

- **WHEN** the run contains no memo
- **THEN** the workspace does not offer a memo download action

### Requirement: Export preserves evidence-first semantics

The Markdown projection SHALL identify counter-evidence, unresolved
requirements, and the non-advisory nature of the output, and SHALL NOT invent
source citations or conclusions.

#### Scenario: Reviewer reads an export

- **WHEN** the exported Markdown is opened outside the application
- **THEN** its evidence ID references and explicit limitations remain visible
