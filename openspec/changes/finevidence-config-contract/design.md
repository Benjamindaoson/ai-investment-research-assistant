## Context

`create_app()` chooses `HttpEvidenceProvider` when an environment URL exists and
otherwise chooses the explicitly synthetic `DeterministicEvidenceProvider`.
The external handoff uses `FIN_EVIDENCE_BASE_URL`; the repository historically
used `FINEVIDENCE_BASE_URL`.

## Goals / Non-Goals

**Goals:**

- Make the documented variable select the external provider.
- Preserve existing local scripts through a temporary compatibility alias.
- Keep provider failures observable; no fallback behavior changes.

**Non-Goals:**

- No changes to FinEvidence endpoints or response models.
- No new secrets, config files, or dependency.

## Decisions

- Resolve canonical `FIN_EVIDENCE_*` first, then legacy `FINEVIDENCE_*` only when
  the canonical variable is absent.
- Use the same precedence for the timeout.
- Test both canonical and alias selection through the application factory.

## Risks / Trade-offs

- Keeping aliases prolongs the old spelling → documentation will mark it as
  compatibility-only, while canonical examples use `FIN_EVIDENCE_*`.
- An unset URL still selects deterministic mode → this remains intentional for
  offline tests and is explicitly labelled in runtime documentation.

## Migration Plan

Update local environment and deployment configuration to `FIN_EVIDENCE_BASE_URL`
and `FIN_EVIDENCE_TIMEOUT_SECONDS`. Remove compatibility aliases in a future
breaking configuration release.
