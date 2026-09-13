## ADDED Requirements

### Requirement: Financial analysis exposes an auditable calculation ledger
The runtime SHALL expose a typed calculation ledger alongside every newly generated financial analysis result. Each ledger entry MUST identify the metric, a human-readable formula, normalized decimal inputs, the calculated output or null, the unit, and an explicit `AVAILABLE` or `UNAVAILABLE` status.

#### Scenario: Available metric records reproducible arithmetic
- **WHEN** the financial tool calculates revenue growth from current and prior revenue
- **THEN** the result includes an `AVAILABLE` ledger entry whose inputs, formula, unit, and output correspond to the returned revenue growth metric

#### Scenario: Missing input is visible rather than omitted
- **WHEN** a metric cannot be calculated because a required input is absent
- **THEN** the result includes an `UNAVAILABLE` ledger entry with a non-empty reason and a null output, and the metric remains listed in `unavailable_metrics`

#### Scenario: Zero denominator is safe and explicit
- **WHEN** a margin calculation receives a zero revenue denominator
- **THEN** the runtime returns no numeric margin, records an `UNAVAILABLE` ledger entry with a zero-denominator reason, and does not raise a division error

### Requirement: Calculation ledger preserves evidence and deterministic identity
The calculation ledger SHALL preserve the existing financial analysis `input_hash` and field-level evidence ID mapping, and serializing the same snapshot twice MUST produce identical ledger entries and input hash.

#### Scenario: Evidence links remain attached to analysis fields
- **WHEN** a caller records an evidence-linked financial analysis
- **THEN** the persisted result contains both the original evidence IDs and the calculation ledger without replacing or fabricating evidence links

#### Scenario: Same snapshot produces stable audit output
- **WHEN** the same decimal financial snapshot is analyzed more than once
- **THEN** the returned input hash and calculation ledger are byte-stably equivalent after canonical JSON serialization

### Requirement: Historical results remain readable
The runtime and frontend SHALL accept historical financial analysis payloads that do not contain a calculation ledger, and SHALL render that the audit ledger is unavailable rather than inventing entries.

#### Scenario: Legacy artifact is read without fabricated calculations
- **WHEN** a persisted analysis result has no `calculation_ledger` field
- **THEN** the result remains readable with an empty ledger and no synthetic formula or output is created

### Requirement: Calculation ledger is read-only in the analyst workspace
The frontend SHALL render ledger entries from the typed service response and SHALL NOT recalculate, edit, or substitute values in the browser.

#### Scenario: Analyst can inspect calculation provenance
- **WHEN** a runtime run has a financial analysis result with ledger entries
- **THEN** the workspace displays each metric's formula, inputs, output, unit, and availability state as read-only information
