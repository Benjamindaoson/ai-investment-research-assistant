## Context

`create_app()` already chooses the evidence provider, planner, synthesizer, and tool registry at startup. Its health route only reports that the HTTP service is alive, while the frontend cannot distinguish a real evidence-backed run from the deterministic local fixture path.

## Goals / Non-Goals

**Goals:**

- Make the selected runtime boundary observable through the existing health route.
- Preserve provider names without exposing credentials or endpoint secrets.
- Validate health metadata at the frontend boundary and show explicit loading/error states.

**Non-Goals:**

- No provider selection changes, health probes to FinEvidence, or live model call.
- No claim that a healthy service means evidence quality or investment correctness.

## Decisions

1. Extend `/api/v1/health` rather than add a second capability endpoint; health remains the single startup/readiness read.
2. Return identity and mode only: `LIVE_EXTERNAL` versus `DETERMINISTIC_FIXTURE`, planner/synthesizer names, and registered tools. Do not return base URLs or secret-derived values.
3. Fetch health independently through the existing service/repository/query layers and render it on the run page. A health failure is visible but does not hide an already-loaded run projection.

## Risks / Trade-offs

- [Risk] A healthy provider can still return insufficient evidence → Mitigation: retain qualification, trace, and evaluation surfaces as the authority for run quality.
- [Risk] Custom injected providers may not expose all optional identity fields → Mitigation: use explicit bounded fallbacks such as the provider class name.

## Migration Plan

No migration. The added JSON fields are additive and older clients can ignore them. Rollback removes the readiness read and leaves execution unchanged.
