## ADDED Requirements

### Requirement: Scenario inputs are explicit and evidence-linked

The runtime SHALL accept exactly one Bull, one Base, and one Bear assumption
set, and every required input field MUST reference at least one qualified
evidence record already persisted on the same research run.

#### Scenario: Complete scenario input is accepted

- **WHEN** an analyst submits three uniquely named scenarios with base revenue,
  growth, FCF margin, discount rate, terminal growth, net cash, shares, and
  field-level evidence IDs
- **THEN** the runtime accepts the input only when all referenced evidence IDs
  exist in the run and have `QUALIFIED` status

#### Scenario: Missing or unqualified links are rejected

- **WHEN** a scenario omits a required evidence link or references missing or
  unqualified evidence
- **THEN** the runtime rejects the request without persisting a valuation
  artifact

### Requirement: Valuation calculations are transparent and deterministic

The runtime SHALL calculate each scenario with Decimal arithmetic using the
documented revenue, FCF, terminal-value, equity-value, and per-share formulas;
it MUST reject non-positive shares or a discount rate that is not greater than
terminal growth.

#### Scenario: Three scenarios produce comparable outputs

- **WHEN** valid Bull, Base, and Bear inputs are supplied
- **THEN** the result contains one calculated output per scenario, the exact
  input hash, the formulas' input values, and no model-inferred fields

#### Scenario: Invalid terminal spread is rejected

- **WHEN** a scenario has a discount rate less than or equal to terminal
  growth, or shares outstanding are zero
- **THEN** the runtime returns a validation error and does not save a partial
  result

### Requirement: Scenario artifacts are durable and reviewable

The runtime SHALL persist a run-scoped scenario artifact, emit an append-only
recording event, and expose the same artifact through a POST write endpoint and
GET read endpoint.

#### Scenario: Artifact is read back after recording

- **WHEN** a valid scenario analysis is recorded for a run
- **THEN** `GET /api/v1/research-runs/{run_id}/valuation-scenarios` returns the
  same input hash, scenario names, outputs, evidence links, and provenance

#### Scenario: Missing artifact remains explicit

- **WHEN** a run has no recorded scenario artifact
- **THEN** the GET endpoint returns HTTP 404 rather than an empty or fabricated
  valuation
