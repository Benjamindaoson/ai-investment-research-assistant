## Context

The backend `ResearchTask` includes `purpose`, `depends_on`,
`evidence_requirements`, and state. Each `EvidenceRequirement` includes an ID,
description, minimum record count, and required stances. The current frontend
schema intentionally parses only a minimal task shape.

## Goals / Non-Goals

**Goals:**

- Make the execution contract inspectable at the run boundary.
- Preserve explicit dependency and evidence-gate semantics.
- Keep old responses compatible and never infer omitted details.

**Non-Goals:**

- No client-side DAG scheduling or task editing.
- No replacement of FinEvidence qualification.

## Decisions

- Add optional detailed fields to the existing runtime task schema and a small
  evidence-requirement schema.
- Reuse the current task list and render details inside each task record.
- Show an unavailable message for historical task records without details.

## Risks / Trade-offs

- Historical responses may omit contract details → optional parsing preserves
  the run and makes the omission visible.
- Requirement status is a backend concern → display IDs and missing IDs only;
  do not locally mark requirements qualified.

## Migration Plan

No migration. This is a frontend read-path enhancement.
