## ADDED Requirements

### Requirement: Synthesis is a replaceable structured boundary
The runtime SHALL support a deterministic synthesis implementation and an explicitly configured structured LLM implementation behind the same boundary.

#### Scenario: Default remains locally runnable
- **WHEN** no LLM synthesizer is configured
- **THEN** the runtime synthesizes claims and thesis deterministically without requiring an API key

#### Scenario: Explicit LLM configuration is honored
- **WHEN** `DEEPRESEARCH_SYNTHESIZER=llm` and all required provider settings are present
- **THEN** the API constructs the structured LLM synthesizer and uses it for synthesis

### Requirement: Model synthesis cannot bypass evidence contracts
The runtime MUST reject synthesis output that references unknown tasks, unknown evidence, or evidence that is not `QUALIFIED`, and MUST preserve runtime-owned claim status and verification.

#### Scenario: Unknown evidence is rejected
- **WHEN** the synthesis adapter returns a claim linked to an evidence ID not present in the run
- **THEN** synthesis fails with an explicit provider/contract error and the run is not reported as successfully completed

#### Scenario: Unqualified evidence is rejected
- **WHEN** the synthesis adapter returns a claim linked to `NEEDS_REVIEW` or `UNQUALIFIED` evidence
- **THEN** synthesis rejects the output before creating a qualified claim

#### Scenario: Claim verification remains external
- **WHEN** a structured claim has valid qualified evidence links
- **THEN** the runtime still invokes the configured external verifier before marking the claim `QUALIFIED`

### Requirement: LLM synthesis is auditable and bounded
The LLM adapter SHALL validate a strict JSON response, preserve request/response hashes, include counter-evidence in its input context, and fail explicitly on transport or contract errors.

#### Scenario: Valid structured response is accepted
- **WHEN** the provider returns a valid bounded JSON synthesis for all research tasks
- **THEN** the runtime receives structured claims and bull/base/bear thesis fields with provider provenance

#### Scenario: Invalid response is visible
- **WHEN** the provider returns malformed JSON, a non-JSON content envelope, or an HTTP/transport error
- **THEN** the adapter raises an explicit synthesis provider error and does not fabricate a thesis
