## Context

FinEvidence v1 exposes evidence verification as a separate endpoint. The
runtime already has a typed client method but does not call it while turning
qualified evidence into claims.

## Goals / Non-Goals

**Goals:**

- Keep external claim verification owned by FinEvidence.
- Preserve the distinction between qualified evidence and a supported claim.
- Make unsupported claims visible in the run state and memo review status.
- Preserve deterministic-provider behavior without network calls.

**Non-Goals:**

- Reimplement verification heuristics in the runtime.
- Treat model confidence as verification.
- Verify claims that have no qualified evidence.

## Decisions

Add an optional verify_claim method to the HTTP evidence adapter. It delegates
to the existing typed FinEvidenceClient.verify endpoint and returns the
provider's supported boolean.

During synthesis, only a provider exposing verify_claim is consulted. A false
response changes the claim to NEEDS_REVIEW. The run completion transition
requires both all task requirements and all claims to be qualified. Provider
transport or response-contract errors are caught at the execution boundary,
persisted as RUN_FAILED, and never silently downgraded to a successful result.

The deterministic provider does not expose this method, so local deterministic
evaluation remains offline and unchanged.

## Risks / Trade-offs

- [Extra external calls] → Verify only claims with qualified evidence and keep
  the existing bounded task plan.
- [Provider unavailable during synthesis] → Persist FAILED with the original
  error context so the run is retryable by the existing case/run workflow.

## Migration Plan

This is additive for deterministic runs. External-provider runs gain a
verification step; existing persisted runs remain readable because no domain
schema migration is required.
