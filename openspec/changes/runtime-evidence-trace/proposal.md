## Why

The runtime backend returns qualified evidence with provenance, but the frontend
currently collapses it to counts and a few labels. An analyst cannot inspect the
source passage or distinguish supporting, counter, conflicting, and unqualified
records while reviewing a thesis.

## What Changes

- Preserve the runtime EvidenceRecord fields through the typed client boundary.
- Add an evidence trace panel to the runtime run workspace.
- Display stance, qualification, source identity, excerpt, locator, and
  provenance completeness without inventing missing data.
- Keep source links and hashes read-only and use the existing backend response.

## Capabilities

### New Capabilities

- `runtime-evidence-trace`: Inspect run evidence and its provenance in context.

### Modified Capabilities

## Impact

Frontend runtime schemas, run workspace, styles, and tests. No new retrieval,
RAG, FinEvidence endpoint, backend model, or database change.
