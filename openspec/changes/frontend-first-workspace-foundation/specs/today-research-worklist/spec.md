## ADDED Requirements

### Requirement: Today research operations view
The Today route SHALL present research work grouped by attention status, active research, review, and completion alongside a compact operational context panel.

#### Scenario: Continue an active research item
- **WHEN** a user activates the continue action on an active research item
- **THEN** the application SHALL navigate to that item's research case route

#### Scenario: Review compact operations context
- **WHEN** a user views the Today route on desktop
- **THEN** the application SHALL show research count, coverage, trigger distribution, and recently completed research in a right-hand context panel

### Requirement: New research entry point
The Today route SHALL provide a visible New Research control that opens the New Research route.

#### Scenario: Begin new research
- **WHEN** a user activates New Research
- **THEN** the application SHALL display an input form for a research question, scope, companies, time range, and attachments
