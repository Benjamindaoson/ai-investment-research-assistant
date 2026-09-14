## ADDED Requirements

### Requirement: Task tools resolve through an explicit registry

The runtime SHALL resolve each `ResearchTask.tool_name` through a registered
tool before invoking evidence collection. A registered tool MUST expose a
callable evidence collection operation.

#### Scenario: Registered tool is selected

- **WHEN** a task declares a registered tool name
- **THEN** the runtime invokes that registered provider and records its provider
  identity in the execution receipt

#### Scenario: Provider-specific qualification is preserved

- **WHEN** two task tool names resolve to providers with different qualification
  authorities
- **THEN** each task is qualified using the authority of its resolved provider

### Requirement: Unknown tools fail explicitly

The runtime MUST reject an unregistered task tool before provider work and SHALL
persist a `FAILED` ToolExecution receipt with an explicit unknown-tool
diagnostic.

#### Scenario: Unknown tool cannot silently use a fallback

- **WHEN** a task declares a tool name absent from the registry
- **THEN** the task does not invoke any provider, its receipt is `FAILED`, and
  the run is `FAILED` with the unknown tool name preserved in the diagnostic

### Requirement: Existing single-provider callers remain compatible

When no explicit registry is supplied, the runtime SHALL register the existing
deterministic, external, and research aliases against the constructor provider.

#### Scenario: Existing deterministic task executes

- **WHEN** a caller constructs `ResearchEngine` with only the existing provider
  argument and a `deterministic-research` task
- **THEN** the task executes through the compatibility registry with unchanged
  evidence and claim semantics

### Requirement: Verification follows task tool selection

When the resolved task provider exposes `verify_claim`, the runtime SHALL use
that provider for claim verification and SHALL NOT invoke a different global
provider.

#### Scenario: Claim uses its task provider

- **WHEN** a qualified claim belongs to a task whose registered provider exposes
  claim verification
- **THEN** verification is invoked on that provider and its durable receipt
  identifies the same provider
