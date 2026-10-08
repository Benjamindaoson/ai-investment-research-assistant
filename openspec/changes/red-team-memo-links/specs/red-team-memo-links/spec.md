## ADDED Requirements

### Requirement: Investment memos preserve Red-team review references

The runtime SHALL append every accepted Red-team review ID to the current
InvestmentMemo without removing prior IDs or copying unstructured reviewer
prose.

#### Scenario: Saved review is linked to the memo

- **WHEN** a valid Red-team review is recorded for a run with a memo
- **THEN** the returned and persisted memo contains that review ID

#### Scenario: Historical memo remains readable

- **WHEN** a stored memo has no Red-team review ID field
- **THEN** the runtime loads it with an empty list and does not fabricate a
  review reference

### Requirement: Red-team memo references are visible in exports

The typed analyst workspace and Markdown memo export SHALL expose the
Red-team review IDs from the memo projection without inventing review content.

#### Scenario: Analyst inspects memo provenance

- **WHEN** a memo contains Red-team review IDs
- **THEN** the workspace and Markdown export show the count or IDs
