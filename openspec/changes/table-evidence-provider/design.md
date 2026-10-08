## Context

The runtime's `HttpEvidenceProvider` currently retrieves through
`/api/v1/evidence/search`, then calls frozen coverage and citation endpoints.
FinEvidence also exposes metadata-first `/api/v1/table/query`; keeping this
path unavailable forces financial tasks to use broad search or manual input.

## Goals / Non-Goals

**Goals:**

- Make table lookup a first-class registered evidence provider.
- Preserve the same `ResearchTask → provider → EvidenceRecord` contract and
  external qualification authority.
- Use requirement entity/metric/period slots to form exact table queries.

**Non-Goals:**

- No semantic TableIR import, SQL, table parsing, value coercion, or
  calculation.
- No new API route; task execution remains the durable entry point.
- No automatic replacement of the search provider for existing plans.

## Decisions

1. Refactor `HttpEvidenceProvider` collection into a reusable retrieval step;
   `HttpTableEvidenceProvider` overrides only retrieval with `table_query`.
   Coverage and citation processing remain shared, preventing two qualification
   implementations.

2. Select the first explicit requirement entity/metric/period, falling back to
   the case target for entity and leaving unspecified filters absent. A task
   with multiple requirements still sends each requirement through the same
   coverage contract; the table query is a bounded candidate retrieval, not a
   semantic answer.

3. When `create_app` constructs a real `HttpEvidenceProvider` from
   `FIN_EVIDENCE_BASE_URL`, create a registry containing the compatibility
   aliases plus `financial-table`. An explicitly supplied registry remains the
   write authority and is never augmented implicitly.

## Risks / Trade-offs

- [Table query returns no rows] → Preserve an empty result and let task
  coverage/replanning handle insufficiency.
- [The first requirement is not representative of all slots] → Keep provider
  scope to bounded task retrieval and document that multi-requirement semantics
  are qualified downstream; a future planner can split tasks explicitly.
- [External service is unavailable] → Existing transport failures and durable
  attempt semantics remain unchanged.
