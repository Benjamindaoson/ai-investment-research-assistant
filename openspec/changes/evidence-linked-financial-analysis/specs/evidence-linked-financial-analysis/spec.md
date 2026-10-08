## ADDED Requirements

### Requirement: Financial calculations are evidence-linked

The runtime MUST accept evidence-backed financial analysis only when every
non-null numeric snapshot field has one or more evidence IDs mapped to it, and
every mapped ID is a QUALIFIED evidence record in the requested run.

#### Scenario: Qualified financial facts are calculated

- GIVEN a completed run with qualified evidence
- AND an explicit Decimal snapshot maps each supplied numeric field to that evidence
- WHEN evidence-backed analysis is requested
- THEN the runtime returns the Decimal calculation result
- AND the result preserves the field-to-evidence mapping

### Requirement: Missing and unqualified facts remain explicit

The runtime MUST reject missing, unknown, or unqualified evidence links and
MUST NOT calculate a result from an unverified fact.

#### Scenario: Unqualified evidence is supplied

- GIVEN an evidence ID exists in the run but is NEEDS_REVIEW
- WHEN it is mapped to a financial field
- THEN the request fails with a clear validation error

### Requirement: No implicit table parsing

The runtime MUST require explicit numeric snapshot values and MUST NOT infer
financial numbers from arbitrary evidence excerpts or table text.

#### Scenario: Table text has no semantic value contract

- GIVEN table evidence has only a textual payload
- WHEN no explicit numeric snapshot value is supplied
- THEN the runtime does not invent a financial fact or calculation.
