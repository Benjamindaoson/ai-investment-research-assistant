## Why

The runtime can optionally ask an LLM to build a research plan, but its claim and thesis synthesis is still hard-coded text. That makes the product useful as a contract demo, not yet as an evidence-qualified analyst surface. A structured synthesis boundary is the smallest step that adds model value without allowing untrusted model prose to bypass runtime validation or human review.

## What Changes

- Add a replaceable synthesis interface with a deterministic default.
- Add an OpenAI-compatible structured LLM synthesis adapter for claims and bull/base/bear thesis fields.
- Validate every model claim against the run's tasks and qualified evidence IDs.
- Preserve runtime-owned claim status, external verification, memo construction, and human approval.
- Configure the adapter through explicit `DEEPRESEARCH_SYNTHESIZER=llm` settings and keep missing configuration fail-fast.

## Capabilities

### New Capabilities

- `structured-synthesis`: Evidence-qualified structured claim and thesis synthesis.

### Modified Capabilities

## Impact

- Backend synthesis boundary, engine wiring, API configuration, and domain validation.
- New backend adapter tests with a local fake HTTP server; no paid model call is required.
- No frontend contract change, database migration, or FinEvidence change.
