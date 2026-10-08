## ADDED Requirements

### Requirement: Analyst can enter explicit scenario assumptions

The runtime workspace SHALL expose editable base revenue and Bull, Base, and
Bear assumption fields as decimal-string inputs, without model-generated
values.

#### Scenario: Empty form does not submit

- **WHEN** the workspace has qualified evidence but one or more numeric fields
  or evidence selectors are empty
- **THEN** the submit control remains disabled and no request is sent

#### Scenario: Complete form submits typed assumptions

- **WHEN** the analyst enters all required values and selects qualified
  evidence for the base revenue and each scenario
- **THEN** the frontend posts a `ScenarioValuationInput` with all three
  scenarios and field-level evidence links

### Requirement: Form state reflects durable API outcomes

The workspace SHALL show a submitting state, preserve the backend error when
submission fails, and update the cached run with the returned valuation
artifact after success.

#### Scenario: Backend rejection remains visible

- **WHEN** the valuation endpoint returns an error
- **THEN** the form shows that error and does not claim that a valuation was
  saved

#### Scenario: Successful submission updates the run

- **WHEN** the valuation endpoint returns a valid artifact
- **THEN** the workspace displays the artifact from the query cache and shows a
  success acknowledgement

### Requirement: Unsafe run states cannot create new valuation work

The frontend SHALL not offer valuation submission for failed, cancelled, or
blocked runs.

#### Scenario: Blocked run is read-only

- **WHEN** a run is `BLOCKED`
- **THEN** the workspace shows existing trace information but does not render
  the valuation input form
