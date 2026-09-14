## Context

The runtime already calculates reported financial ratios from an explicit
snapshot and persists that artifact on a research run. The next useful analyst
capability is a bounded scenario bridge that makes operating assumptions and
valuation mechanics inspectable without pretending to be a market-data or
portfolio system.

## Goals / Non-Goals

**Goals:**

- Accept exactly three explicitly named Bull, Base, and Bear scenario inputs.
- Require field-level evidence links to qualified evidence in the same run.
- Calculate a small transparent terminal-value model with `Decimal` values.
- Persist and expose the result as a run-scoped artifact.
- Keep missing data and invalid assumptions as explicit validation failures.

**Non-Goals:**

- No price feed, comparable-company database, DCF forecasting engine, tax
  inference, currency conversion, or trading action.
- No model-generated assumptions and no automatic defaulting of missing inputs.
- No changes to FinEvidence or imports from its internals.

## Decisions

1. **Use one run-scoped input contract.** `ScenarioValuationInput` contains a
   base revenue, three `ScenarioAssumption` objects, and an evidence-ID map.
   This keeps the write boundary explicit and avoids a second persistence
   abstraction.
2. **Use percentage points as Decimal strings.** A value of `10` means 10%.
   Formulas divide by 100 inside the calculation tool, while JSON remains
   lossless and consistent with existing financial artifacts.
3. **Use an illustrative terminal-value bridge.** For each scenario:
   `projected revenue = base revenue × (1 + growth / 100)`, `FCF = projected
   revenue × FCF margin / 100`, `terminal value = FCF / (discount rate / 100 −
   terminal growth / 100)`, `equity value = terminal value + net cash`, and
   `value per share = equity value / shares`. The rate spread must be positive.
4. **Persist the computed artifact on `ResearchRun`.** The engine remains the
   write authority, validates all evidence IDs and qualification states, and
   emits `VALUATION_SCENARIOS_RECORDED` for auditability.
5. **Render read-only output in the runtime workspace.** Inputs remain a
   future dedicated analyst form; this slice proves the contract and output
   surface without inventing an interaction model.

## Risks / Trade-offs

- [Risk] A terminal-value bridge can be mistaken for a price target →
  Mitigation: label it illustrative, show assumptions/formulas, and keep it
  review-gated with explicit provenance.
- [Risk] A caller links a real but irrelevant evidence record → Mitigation:
  the runtime validates existence and qualification; semantic relevance stays
  a human/evidence-provider responsibility.
- [Risk] Existing runs do not have the new field → Mitigation: nullable
  additive payload field and a 404 until the artifact is explicitly recorded.

## Migration Plan

Additive Pydantic and JSON payload changes require no database migration. Older
run payloads load with `valuation_scenarios = null`; new callers use the POST
endpoint and can read the artifact back through GET.
