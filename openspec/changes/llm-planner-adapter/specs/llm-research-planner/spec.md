## ADDED Requirements

### Requirement: LLM planner output is structured and untrusted

The LLM planner SHALL request JSON-only task output, validate the response against the ResearchTask contract, and return a ResearchPlan draft that still requires the ResearchEngine's canonical case, hash, DAG, and evidence validation.

#### Scenario: Valid structured output becomes a plan draft

- **WHEN** the configured provider returns valid JSON containing evidence-bearing tasks
- **THEN** the adapter returns a ResearchPlan draft with local planner metadata and input hash

#### Scenario: Free-form or malformed output is rejected

- **WHEN** the provider returns non-JSON content, missing tasks, or a task that violates the domain contract
- **THEN** the adapter raises an explicit planner contract error and returns no plan

### Requirement: LLM planner calls are auditable without storing secrets

The planner SHALL record provider/model identity and request/response content hashes in plan provenance, and SHALL never include the API key in returned objects, logs, or persisted plan data.

#### Scenario: Request and response hashes are available

- **WHEN** an LLM plan is accepted
- **THEN** the plan provenance contains provider, model, request hash, and response hash

#### Scenario: API key is not persisted

- **WHEN** a plan is serialized after an LLM call
- **THEN** no secret value appears in the plan metadata or provenance

### Requirement: LLM use is explicit and failures are not hidden

The runtime SHALL use the LLM planner only when explicit configuration selects it. If selected and the provider fails, the runtime SHALL return an explicit error rather than silently using a deterministic plan.

#### Scenario: Default startup remains deterministic

- **WHEN** LLM mode is not explicitly enabled
- **THEN** the runtime uses the deterministic planner without making an external model request

#### Scenario: Selected provider times out

- **WHEN** LLM mode is enabled and the provider exceeds its timeout
- **THEN** the planner raises an explicit timeout/provider error and no run is created from a fallback plan
