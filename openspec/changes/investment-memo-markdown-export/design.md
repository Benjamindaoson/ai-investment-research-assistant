## Context

`RuntimeMemo` already contains structured sections, claim IDs, evidence IDs,
counter-evidence IDs, unresolved requirement IDs, status, and provenance. The
run page also has the run identifier and state. These fields are sufficient for
a faithful text projection.

## Goals / Non-Goals

**Goals:**

- Produce stable Markdown from the current in-memory, server-validated data.
- Make evidence and unresolved requirements visible in the export.
- Use the browser download API with no dependency or backend endpoint.
- Keep export available only when a memo is present.

**Non-Goals:**

- No PDF/DOCX rendering, formatting engine, or remote storage.
- No new claims, citations, financial facts, or investment recommendation.
- No mutation of the runtime or memo.

## Decisions

1. Keep serialization in a pure function so exact output is testable and the
   download component remains thin.
2. Use a filename derived from the run ID with non-word characters replaced,
   preventing path-like names from entering the download attribute.
3. Label the output as a projection and include the memo's evidence ID lists;
   source citation resolution remains the FinEvidence boundary's responsibility.

## Risks / Trade-offs

- [Risk] Markdown cannot preserve every future rich memo format → Mitigation:
  export the canonical structured fields and leave richer formats for a later
  explicit capability.
- [Risk] Browser download APIs may be unavailable in test/non-browser contexts
  → Mitigation: isolate the API call behind the click handler; serialization is
  independently testable.

## Migration Plan

No migration. This is a local projection of already persisted data.

## Open Questions

None for Markdown. PDF/DOCX export needs a separate product decision.
