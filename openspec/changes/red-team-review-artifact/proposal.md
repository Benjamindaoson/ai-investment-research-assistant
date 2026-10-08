## Why

Counter-evidence is collected and shown in memo sections, but the runtime
does not preserve the analyst's explicit challenge to the thesis. Without a
red-team artifact, a later reviewer cannot tell which assumption was attacked,
which evidence was used, or whether the challenge requires more research.

## What Changes

- Add a durable RedTeamReview domain record attached to a run and thesis.
- Add API endpoints to create and list red-team reviews.
- Require cited evidence to exist in the run and be counter or conflicting.
- Make a REQUIRES_RESEARCH outcome put the thesis back into review.
- Expose the records through the typed runtime projection and workspace.

## Capabilities

### New Capabilities

- red-team-review-artifact: Record auditable thesis challenges and outcomes.

### Modified Capabilities

## Impact

ResearchRun domain persistence, runtime write authority, FastAPI routes,
frontend runtime schema, and tests. No FinEvidence changes and no new
dependency.
