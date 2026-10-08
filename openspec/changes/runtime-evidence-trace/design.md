## Context

The backend EvidenceRecord already contains source identity, excerpt,
provider, locator, content hash, and qualification. The runtime frontend schema
only retains a minimal subset, so the primary review surface cannot audit what
supports a claim.

## Goals / Non-Goals

**Goals:**

- Preserve and display evidence fields returned by the runtime.
- Keep missing provenance visibly missing rather than fabricating citations.
- Make evidence stance and qualification scannable for thesis review.

**Non-Goals:**

- No client-side search, chunking, ranking, or RAG implementation.
- No mutation or requalification control in the frontend.
- No direct import from FinEvidence or changes to its API.

## Decisions

- Extend the existing `runtimeRunSchema` evidence object with optional source
  fields for backwards-compatible reads. Required identity fields remain
  validated.
- Render one read-only record per evidence item in the run workspace. Use
  source URLs only as links and show locator/content hash as observed metadata.
- Derive a simple provenance-complete display flag from the same three fields
  used by the backend (`source_url`, `locator`, and `content_hash`). This is a
  display aid, not a second qualification rule.

## Risks / Trade-offs

- [Older responses omit detailed fields] → Keep details optional and show a
  clear unavailable label.
- [Long excerpts reduce scanability] → Use bounded CSS line clamping only for
  display; the response remains unchanged and inspectable in the source link.

## Migration Plan

No migration. The frontend can read both minimal historical responses and full
current EvidenceRecord responses.

## Open Questions

Evidence pagination belongs to a future high-volume API; the current run
contract returns a bounded evidence set.
