## Context

`HttpEvidenceProvider` already implements the frozen v1 sequence, but unit
tests replace `urlopen` and therefore cannot prove deployment wiring, catalog
read-back, or citation identity against a real service. FinEvidence may be
empty, partial, or slow; the integration check must preserve those states
without turning data availability into an unsupported quality claim.

## Goals / Non-Goals

**Goals:**

- Run the full provider chain through the public HTTP client only.
- Make the test opt-in through `FIN_EVIDENCE_INTEGRATION=1` and
  `FIN_EVIDENCE_BASE_URL`.
- Assert stable contract invariants: API version, evidence identity, citation
  identity, source locator, content hash, and runtime provenance.

**Non-Goals:**

- No changes to FinEvidence or its catalog.
- No assertion that a specific query is eligible; `PARTIAL` and empty search
  are legitimate observed outcomes.
- No network call during the default backend test suite.

## Decisions

1. Use a pytest integration marker and skip unless explicitly enabled. This
   keeps normal CI deterministic while making the real check one command away.

2. Use a broad, known catalog query (`HSBC`) with a bounded top-k and one
   context requirement. The test asserts object/citation consistency rather
   than a fragile specific metric result.

3. Exercise `HttpEvidenceProvider.collect`, not private FinEvidence modules.
   The runtime receives only `EvidenceRecord` objects and checks the same
   provenance fields used by normal execution.

## Risks / Trade-offs

- [The local service is slow or unavailable] → The test is opt-in, uses the
  configured client timeout, and fails with the transport diagnostic.
- [Catalog contents change] → Assertions target schema and identity invariants,
  not document count, score, or investment conclusion.
- [A broad query returns no evidence] → The smoke records a clear empty result;
  it fails only if the service response violates the v1 contract.
