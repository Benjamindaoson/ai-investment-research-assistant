## ADDED Requirements

### Requirement: Financial facts must be explicit and evidence-linked

The runtime MUST accept a financial fact only when it contains a supported
snapshot field, a decimal value, period, unit, currency, basis, and at least one
evidence ID. The runtime MUST NOT derive a numeric value from raw evidence
text implicitly.

#### Scenario: Valid reported facts form a snapshot

- **WHEN** a fact set contains one revenue fact and optional supported fields
  with a common period and explicit metadata
- **THEN** the runtime creates a `FinancialSnapshot` with the supplied decimal
  values
- **AND** preserves every fact's evidence IDs and basis in the analysis result.

#### Scenario: Invalid fact set is rejected

- **WHEN** a fact set has duplicate fields, mixed periods, no revenue fact, or
  a negative value for a non-negative snapshot field
- **THEN** the runtime rejects it before calculation or persistence.

### Requirement: Financial facts must use qualified run evidence

The Research Run financial-facts endpoint MUST reject any evidence ID that is
missing from the run or whose qualification is not `QUALIFIED`.

#### Scenario: Qualified facts produce an auditable analysis

- **WHEN** a valid fact set references qualified evidence in the target run
- **THEN** the runtime calculates the existing deterministic metrics and
  calculation ledger
- **AND** persists the financial analysis and typed facts against that run
- **AND** the persisted result can be read after runtime reconstruction.

#### Scenario: Unqualified facts fail closed

- **WHEN** a fact references missing or unqualified evidence
- **THEN** the endpoint returns a validation error
- **AND** no financial analysis artifact is persisted.

### Requirement: FinEvidence remains an external evidence boundary

The typed financial fact capability MUST use only runtime contracts and
qualified evidence IDs. It MUST NOT import FinEvidence internal retrieval,
parser, TableIR, evaluation, CLIP, or benchmark modules.

#### Scenario: Raw evidence text is not silently converted

- **WHEN** an evidence record contains human-readable table or text content
  without a supplied typed decimal fact
- **THEN** the runtime does not use that content as a numeric snapshot value.
