## Decision

Add `metric` and `period` keyword arguments to `FinEvidenceClient.search` and
serialize them through the existing `FinEvidenceFilters` model. The provider
forwards slots only when the task has one requirement; a task with multiple
requirements has no single safe filter tuple and remains a broad search whose
coverage call still receives every requirement.

No optional slot is invented. Explicit requirement values only are forwarded.

## Non-goals

- No query rewriting or fuzzy filter inference.
- No changes to FinEvidence.
- No filtering of coverage or citation requests.
