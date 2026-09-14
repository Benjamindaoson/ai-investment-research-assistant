## Context

During synthesis, a provider that implements `verify_claim` is called for
qualified claims. The call runs under the ResearchEngine lease, but its state
is not represented in `ResearchRun.tool_executions`; only the final Claim state
and run event are durable. Verification is an external side effect and must
therefore use the same pre-call receipt and ownership guard as evidence
collection.

## Goals / Non-Goals

**Goals:**

- Persist a verification attempt before the external call.
- Distinguish HTTP/provider success with `supported=false` from a failed call.
- Preserve UNKNOWN_EFFECT when lease ownership is lost during verification.
- Expose the result through the existing run API and tool trace.

**Non-Goals:**

- No automatic verification retry or reconciliation queue.
- No raw claim text or provider response body in the receipt.
- No changes to FinEvidence or to the claim qualification policy.

## Decisions

1. **Reuse `ToolExecution`.** Add an operation discriminator and optional
   boolean verification result rather than creating a second receipt type. This
   keeps one ordered execution trace and reuses existing persistence, lease,
   and frontend rendering.

2. **Create the receipt inside `_synthesize`.** The engine already owns the
   lease and is the only caller of `verify_claim`; it will persist an
   `UNKNOWN_EFFECT` receipt before calling the provider, then update it after a
   response. The input hash covers the claim statement and evidence IDs, while
   the attempt key includes the run and claim IDs.

3. **Treat negative verification as successful execution.** A provider response
   with `supported=false` is a valid observation. The receipt is `SUCCEEDED`
   with `verification_supported=false`, and the existing claim gate changes the
   Claim to `NEEDS_REVIEW`. Transport, contract, or unexpected provider errors
   remain `FAILED` and fail the run.

4. **Pass lease context through synthesis.** `_execute` passes its lease ID and
   heartbeat event into `_synthesize`; all receipt writes and provider-result
   adoption check ownership. This prevents a stale executor from publishing a
   verification result.

## Risks / Trade-offs

- [Existing custom providers gain an extra receipt] → Only providers exposing
  a callable `verify_claim` create one, preserving deterministic offline runs.
- [Verification is still synchronous] → The receipt makes its state durable;
  worker extraction and provider idempotency remain a later operational step.
- [Failed verification leaves the run failed] → This preserves the existing
  explicit failure semantics and avoids silently treating an unknown result as
  unsupported evidence.
