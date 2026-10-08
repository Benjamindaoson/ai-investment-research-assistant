## Context

The deterministic planner is a reproducible baseline, not the final intelligence layer. A future planner needs to propose a task DAG from a research question, but model output is untrusted input. The adapter must therefore stop at a typed draft, while `ResearchEngine` remains responsible for canonical validation and persistence.

## Goals / Non-Goals

**Goals:**

- Call an OpenAI-compatible chat-completions endpoint through a small standard-library adapter.
- Request JSON-only task output with no financial facts or claims.
- Validate the response shape, hash the request and response, and expose provider/model metadata.
- Make opt-in configuration explicit and preserve deterministic operation by default.

**Non-Goals:**

- Evaluating the truth of model-generated financial claims.
- Letting the model retrieve evidence, execute tools, approve decisions, or bypass DAG validation.
- Adding a model SDK, agent framework, prompt orchestration layer, or automatic provider fallback that could hide failure.

## Decisions

1. **OpenAI-compatible transport via `urllib`.** DeepSeek and other compatible providers can share the adapter without adding an SDK. The transport uses a bounded timeout and emits explicit provider errors.

2. **Draft payload contains tasks only.** The model returns `{\"tasks\": [...]}`. The adapter supplies case ID, question, planner identity/version, and input hash locally, so the model cannot forge provenance metadata.

3. **Explicit opt-in.** `DEEPRESEARCH_PLANNER=llm` is required, along with `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, and `DEEPSEEK_MODEL` (or generic `LLM_*` equivalents). Missing or partial configuration fails fast when selected; absent opt-in uses deterministic planning.

4. **Hash request and response bytes.** Hashes are recorded in the returned plan provenance and do not include the secret. This supports traceability without persisting credentials.

5. **No silent fallback after an LLM call fails.** If the user opted into LLM planning and the call fails, the API returns an explicit failure. Falling back to a deterministic plan would hide a production configuration or provider failure.

## Risks / Trade-offs

- [LLM returns a plausible but incomplete DAG] → Run the existing planner golden evaluation and engine validation before persistence.
- [Provider API schema drift] → Validate the minimal response envelope and report contract errors.
- [Cost or latency surprises] → Require explicit opt-in, bounded timeout, and document that live calls are not part of default tests.
- [Sensitive question content leaves the process] → Make the external call visible through configuration and record hashes only; production data classification remains a deployment responsibility.

## Migration Plan

1. Add the adapter and mocked transport tests.
2. Wire explicit planner selection into `create_app`.
3. Keep deterministic planner as default and run all existing tests/evaluation.
4. Enable LLM mode only in a controlled environment with a configured key and endpoint.
5. Compare LLM plans against the same golden cases before promoting the adapter.

## Open Questions

- The production provider, model, retention policy, and data-classification policy remain deployment decisions.
