## Context

Claim verification already creates durable `ToolExecution` receipts, while evidence records preserve FinEvidence provenance. The trace endpoint currently returns claims but omits the join between claim, verifier receipt, and source evidence. The frontend can download Markdown, but no PDF artifact exists.

## Goals / Non-Goals

**Goals:**

- Return explainable, secret-safe verification summaries.
- Prevent cross-task evidence from silently supporting a claim.
- Preserve `PARTIAL` and `DRAFT` semantics when verification is unsupported.
- Produce a polished local PDF from a persisted run without changing the runtime storage model.
- Compare deterministic and LLM outputs using the same observed FinEvidence endpoint and metrics.

**Non-Goals:**

- Do not weaken external verification gates.
- Do not build a PDF microservice, browser report editor, or new document database.
- Do not infer unsupported financial facts from excerpts.

## Decisions

- Derive explainability from existing `EvidenceRecord` and `ToolExecution` state rather than adding a second receipt table.
- Include verifier boolean/result hash and bounded diagnostic fields, never raw authorization headers or provider payloads.
- Enforce claim evidence scope at the runtime boundary; evidence cited by a claim must belong to that claim's task.
- Use reportlab only in an explicit local export tool. The canonical runtime remains independent of PDF dependencies.
- Mark comparison samples with their catalog observation and run state; a `PARTIAL` LLM run is not promoted to a completed memo.

## Risks / Trade-offs

- [Provider response detail is bounded] -> expose supported/status/hash and coverage metadata, not raw provider payloads.
- [PDF renderer may differ across machines] -> render and inspect the generated artifact locally before delivery.
- [Catalog can change between runs] -> record FinEvidence health/catalog size and label comparison as an observed local snapshot, not a scientific benchmark.
