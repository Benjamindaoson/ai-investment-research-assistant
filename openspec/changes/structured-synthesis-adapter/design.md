## Context

`ResearchEngine._synthesize` currently derives claims and thesis text deterministically from evidence counts. The deterministic path is valuable as a local fixture, but a real analyst needs model-generated interpretation. The model must remain an untrusted proposal: it cannot invent evidence IDs, qualify claims, verify citations, or approve a memo.

## Goals / Non-Goals

**Goals:**

- Provide a structured, replaceable synthesis provider with deterministic and LLM implementations.
- Send only the research case, task contracts, and evidence records needed for synthesis.
- Reject malformed output, unknown evidence IDs, unqualified evidence links, unknown tasks, and missing scenario fields.
- Reuse the existing provider verification step and runtime-generated memo/memory surfaces.

**Non-Goals:**

- No free-form streaming, chat memory, prompt-based evidence qualification, or autonomous investment decision.
- No new model SDK or dependency; use the standard-library HTTP approach already used by the planner.
- No automatic fallback from an explicitly configured LLM failure to deterministic synthesis.

## Decisions

1. Define `ResearchSynthesizer.synthesize(case, run) -> SynthesisDraft` and keep the deterministic implementation inside the runtime boundary. The engine owns validation and verification after the adapter returns.
2. Represent the adapter response with strict Pydantic models: each claim has `task_id`, `statement`, `evidence_ids`, and `confidence`; thesis has statement plus bull/base/bear. The engine assigns claim IDs and statuses rather than trusting the model.
3. Permit only evidence records with `qualification == QUALIFIED` in model claim links. The adapter receives qualified records only, and the engine independently checks returned IDs against the run.
4. Reuse the planner's OpenAI-compatible configuration names (`DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`) and add only the explicit synthesizer selector. Provider request/response hashes remain in provenance for audit.

## Risks / Trade-offs

- [Risk] Structured model output can still be economically wrong → Mitigation: evidence links, external claim verification, counter-evidence in the input, and mandatory human review remain runtime-owned.
- [Risk] Model output can omit a research task → Mitigation: the engine rejects incomplete task coverage instead of silently creating a partial thesis.
- [Risk] LLM provider latency can hold a run lease → Mitigation: existing lease heartbeat protects ownership; in-flight cancellation remains a later worker concern.

## Migration Plan

Default behavior remains deterministic, so existing deployments and persisted runs require no migration. Enable the LLM path only after setting all explicit configuration variables; rollback is one environment change back to deterministic mode.

## Open Questions

The synthesis quality/evaluation matrix, model selection, and financial-domain rubric need a separate scored evaluation phase before an LLM becomes the default.
