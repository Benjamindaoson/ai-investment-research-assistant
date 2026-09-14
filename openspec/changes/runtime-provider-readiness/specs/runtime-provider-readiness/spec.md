## ADDED Requirements

### Requirement: Runtime health identifies execution boundaries

The runtime health response SHALL expose the selected evidence mode, evidence provider identity, planner identity, synthesizer identity, and registered task tools without exposing credentials.

#### Scenario: Deterministic local runtime

- **WHEN** the runtime is constructed without a FinEvidence URL
- **THEN** health reports `DETERMINISTIC_FIXTURE` and the deterministic provider identity

#### Scenario: External evidence runtime

- **WHEN** the runtime is constructed with a FinEvidence URL
- **THEN** health reports `LIVE_EXTERNAL` and the configured external provider identity

### Requirement: Analysts can see readiness context

The live run workspace SHALL display the health boundary independently from run execution and SHALL distinguish provider readiness from research quality.

#### Scenario: Health is available

- **WHEN** a valid health response is returned
- **THEN** the workspace displays the mode, provider, planner, synthesizer, and tool names with a note that health is not an evidence-quality judgment

#### Scenario: Health is unavailable

- **WHEN** the health request fails or its response is invalid
- **THEN** the workspace displays an explicit readiness error while preserving the run page
