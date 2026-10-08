## ADDED Requirements

### Requirement: Frontend consumes runtime artifacts through typed transport

The frontend SHALL expose validated repository methods for runtime memo, target
investment memory, and financial analysis when a runtime URL is configured.

#### Scenario: Runtime returns a valid memo

- **WHEN** the memo endpoint returns a valid payload
- **THEN** the service parses and returns its typed status and evidence links

#### Scenario: Runtime returns invalid data

- **WHEN** an endpoint response violates its Zod contract
- **THEN** the service rejects the response rather than passing malformed data
  to UI code

### Requirement: Financial precision is preserved at the browser boundary

The frontend SHALL send financial numeric fields as decimal strings and SHALL
not recalculate backend metrics in JavaScript.

#### Scenario: Financial analysis request

- **WHEN** a repository caller submits a snapshot
- **THEN** the transport posts the validated snapshot and returns backend
  metrics without local arithmetic
