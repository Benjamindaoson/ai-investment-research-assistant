## Context

The runtime owns qualification of records returned by an external provider. The
provider boundary validates record shape and task ownership, while the runtime
decides whether a record can support a claim. `EvidenceRecord` already exposes
the deterministic `provenance_complete` predicate.

## Goals / Non-Goals

**Goals:**

- Make claim support auditable by construction.
- Preserve incomplete evidence for analyst review instead of dropping it.
- Reuse the existing provenance predicate and state vocabulary.

**Non-Goals:**

- Re-fetching or repairing incomplete sources.
- Source credibility scoring or duplicate detection.
- Changing FinEvidence retrieval responsibilities.

## Decisions

Qualification becomes the conjunction of stance compatibility and complete
provenance. A record that fails either condition is `NEEDS_REVIEW`; this is
conservative and keeps the observed record available to trace/memo consumers.
The change is centralized in `_qualify`, so every task follows the same rule.

## Risks / Trade-offs

- [Risk] A provider that intentionally omits a locator produces more partial
  runs → Mitigation: the trace exposes incomplete provenance counts, and the
  provider contract can be fixed without weakening the runtime gate.

## Migration Plan

No migration is required. Existing stored records retain their historical
qualification; newly executed tasks apply the stricter rule.

## Open Questions

Whether provenance completeness should become a provider-side hard rejection is
deferred until FinEvidence production integration tests exist.
