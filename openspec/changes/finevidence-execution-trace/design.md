## Context

The runtime already persists one `ToolExecution` per research task and exposes
it through the run API and read-only frontend trace. The receipt is durable and
safe for retries, but currently cannot identify the provider used or bind the
result to the exact case/task contract that produced it. The FinEvidence
adapter already preserves source-level provenance on `EvidenceRecord`; this
change adds only execution-level metadata and does not duplicate evidence
storage.

## Goals / Non-Goals

**Goals:**

- Make each evidence collection attempt auditable without storing raw HTTP
  requests or provider responses.
- Keep old persisted runs and clients readable.
- Make empty, qualified, review-needed, and unqualified results distinguishable
  in the receipt.
- Keep the metadata available in the existing API and frontend trace.

**Non-Goals:**

- No FinEvidence repository changes or new endpoint.
- No retry policy, queue, or provider response cache.
- No raw query, evidence excerpt, or model output in `ToolExecution`.

## Decisions

1. **Hash the canonical case/task input.** The engine will derive a SHA-256
   `input_hash` from the serialized case and task immediately before provider
   execution. This binds the receipt to the execution contract while avoiding
   storing sensitive or verbose query text. A new query object is unnecessary
   because the existing task and case models already define the provider input.

2. **Record provider identity and bounded counts.** `provider` and four
   non-negative evidence counters are added with defaults. The counters are
   populated after runtime qualification, so the receipt reflects the same
   qualification gate used by claims and memo generation.

3. **Use additive compatibility defaults.** Backend fields have defaults and
   frontend fields are optional. Existing SQLite JSON and older API payloads
   continue to validate without migration.

4. **Render metadata in the existing trace.** The current read-only component
   will show provider, input hash, and a compact count summary. No new page or
   state layer is warranted.

## Risks / Trade-offs

- [Hash is opaque to a human] → The plan/task trace remains the human-readable
  explanation; the hash supplies deterministic correlation and tamper evidence.
- [Old receipts report zero counters] → Defaults preserve compatibility, and
  only new executions claim complete result counts.
- [Provider name is convention-based] → Unknown providers are recorded as
  `unknown` rather than failing an otherwise valid custom provider.
