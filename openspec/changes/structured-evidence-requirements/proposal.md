## Why

`EvidenceRequirement` currently carries only a description, count, and stance,
so the runtime sends hard-coded semantics to FinEvidence. That weakens the
research contract precisely where evidence qualification depends on fact type,
role, slots, and criticality. The runtime needs to preserve the planner's
structured requirement intent without implementing another retrieval layer.

## What Changes

- Add optional, validated requirement semantics aligned with the frozen
  FinEvidence v1 coverage contract: fact type, role, entity/metric/period
  slots, criticality, and evidence role.
- Make the HTTP provider serialize those task-owned semantics into
  `/api/v1/evidence/coverage` requests instead of hard-coded values.
- Preserve current callers through safe defaults and keep runtime qualification
  and evidence provenance behavior unchanged.
- Surface the structured fields in the live runtime task contract so reviewers
  can see what each requirement means.
- Add contract tests for defaults, validation, HTTP payload propagation, and
  round-trip frontend parsing.

## Capabilities

### New Capabilities

- `structured-evidence-requirements`: Typed requirement semantics are preserved
  from research planning through the FinEvidence coverage boundary.

### Modified Capabilities

## Impact

- `backend/research-runtime/src/deepresearch/domain/models.py` and planner
  prompt/fixtures.
- `backend/research-runtime/src/deepresearch/runtime/evidence.py` and its
  provider contract tests.
- `apps/web/src/services/research-runtime-service.ts` and task-contract UI.
- No FinEvidence source changes, no new dependencies, and no direct imports
  from FinEvidence internals.
