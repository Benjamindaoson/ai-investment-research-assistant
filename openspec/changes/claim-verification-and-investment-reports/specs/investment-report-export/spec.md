## ADDED Requirements

### Requirement: A persisted research run can be exported as a PDF investment memo

The local exporter SHALL include observed run state, memo status, thesis scenarios, evidence quality counts, claim verification outcomes, source provenance, and an explicit human-review disclaimer.

#### Scenario: Completed run is exported

- **WHEN** an analyst exports a persisted completed run
- **THEN** the PDF contains the memo sections, evidence-linked claims, source locators, page numbers, and review status in a readable layout

#### Scenario: Partial run is exported

- **WHEN** an analyst exports a partial run
- **THEN** the PDF clearly labels the memo as draft/partial, lists unresolved or unsupported claims, and does not present the output as approved investment advice
