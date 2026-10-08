## Context

The backend already exposes a typed `ScenarioValuationInput` contract and
validates every evidence link. The workspace has a qualified evidence list and
TanStack Query mutations for neighboring financial artifacts. This change only
needs to make the existing contract usable from the browser.

## Goals / Non-Goals

**Goals:**

- Keep decimal values as strings from browser to backend.
- Let the analyst edit all scenario assumptions explicitly.
- Require a qualified evidence record before submission.
- Update the cached run with the returned durable artifact.
- Surface API errors and preserve the read-only/illustrative warning.

**Non-Goals:**

- No model-generated defaults, price lookup, automatic assumption suggestion,
  or additional evidence retrieval.
- No per-field evidence picker in this first compact form; one selected
  qualified source is deliberately linked to every assumption field and can be
  refined in a later evidence-mapping interaction.

## Decisions

1. Reuse the existing runtime repository and query-cache pattern rather than
   adding a separate state store.
2. Use controlled local form state with empty numeric values, so the UI never
   implies that an assumption is factual before the analyst enters it.
3. Require a global base-revenue evidence selection and one source per
   scenario. The submit mapper writes the exact seven backend evidence keys for
   each scenario.
4. Disable the form for `FAILED`, `CANCELLED`, and `BLOCKED` runs. A blocked run
   must be resolved through its explicit recovery API first.

## Risks / Trade-offs

- [Risk] One source per scenario is less precise than field-level selection →
  Mitigation: the resulting payload still contains field-level links and the
  UI labels the source scope; add per-field selection when analyst feedback
  proves it is needed.
- [Risk] Large forms are easy to submit incorrectly → Mitigation: empty
  initial values, browser number inputs, disabled submit, and API/Zod
  validation remain active.
