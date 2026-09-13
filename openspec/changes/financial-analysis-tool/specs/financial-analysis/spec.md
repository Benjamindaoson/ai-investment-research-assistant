## ADDED Requirements

### Requirement: Financial calculations are deterministic and precise

The calculator SHALL use validated numeric inputs and decimal arithmetic to
compute revenue growth, margins, free cash flow, FCF margin, and net cash.

#### Scenario: Complete snapshot

- **WHEN** all required snapshot values are present and denominators are nonzero
- **THEN** each applicable metric is returned with its canonical input hash

#### Scenario: Negative operating cash flow

- **WHEN** operating cash flow is negative and capex is present
- **THEN** free cash flow is computed as operating cash flow minus capex without
  clamping or hiding the negative result

### Requirement: Undefined calculations remain explicit

The calculator SHALL return `None` and list the metric in
`unavailable_metrics` when an input is missing or a denominator is zero.

#### Scenario: Zero prior revenue

- **WHEN** prior revenue is zero
- **THEN** revenue growth is unavailable rather than infinite or fabricated

#### Scenario: Missing cash flow inputs

- **WHEN** either operating cash flow or capex is missing
- **THEN** free cash flow and FCF margin are unavailable and named in the result
