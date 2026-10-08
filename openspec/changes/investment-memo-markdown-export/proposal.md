## Why

The runtime now produces structured, evidence-linked investment memos, but the
analyst workspace has no portable output. A reviewable Markdown artifact is the
smallest useful export for committee notes, version control, and later
re-checking without introducing a document generation service.

## What Changes

- Add a deterministic client-side Markdown serializer for the current runtime
  memo and its evidence links.
- Add a download action to the runtime workspace when a memo exists.
- Include explicit run state, memo status, thesis, structured sections, and
  provenance references; retain the product disclaimer.

## Capabilities

### New Capabilities

- `investment-memo-markdown-export`: Download a reviewable Markdown projection
  of a durable runtime memo.

### Modified Capabilities

- None.

## Impact

Frontend-only utility, component, and runtime workspace changes. No backend,
database, FinEvidence, or new dependency changes.
