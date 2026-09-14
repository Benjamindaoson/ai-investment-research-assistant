## Context

FinEvidence is an external evidence authority. The investment research runtime
must consume it only through the frozen v1 HTTP API and must not treat an empty
or synthetic response as proof that the external chain works.

## Decision

Use one opt-in pytest module for two levels of verification:

1. adapter-level search assertions require a non-empty real response;
2. API-level assertions run the default deterministic planner through
   `create_app()` with `FIN_EVIDENCE_BASE_URL` configured and verify that every
   returned record is owned by `finevidence-http` and carries complete
   provenance.

The table call remains part of the adapter smoke, but its result may be empty
for a broad query. This tests correct routing and empty-result handling without
inventing data requirements.

The test is skipped unless `FIN_EVIDENCE_INTEGRATION=1` and
`FIN_EVIDENCE_BASE_URL` are present. This preserves a fast, offline default
suite while making the live command explicit and reproducible.

## Non-goals

- No changes to FinEvidence.
- No direct imports from FinEvidence Python packages.
- No assertion that every research question has table evidence.
- No paid model calls.
