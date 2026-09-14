## Why

The deterministic fallback planner has the right task topology but its
evidence requirements are generic descriptions. That weakens FinEvidence
coverage alignment and gives later financial extraction no reliable semantic
contract to consume.

## What Changes

- Keep the bounded three-task DAG and stable task IDs.
- Add explicit entity, role, fact type, criticality, evidence role, and stance
  semantics to market, fundamentals, and downside requirements.
- Make fundamentals a critical value-support requirement and risk a critical
  counter-evidence requirement.
- Preserve deterministic defaults and existing planner/evaluation behavior.

## Capabilities

### New Capabilities

- `semantic-research-plan`: The fallback research plan emits meaningful,
  evidence-aligned requirement contracts.

### Modified Capabilities

## Impact

- Deterministic planner output and planner contract tests/docs only.
- No new task types, dependencies, provider behavior, FinEvidence changes, or
  LLM calls.
