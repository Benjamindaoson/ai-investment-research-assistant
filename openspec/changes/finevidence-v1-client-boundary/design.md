## Boundary

`FinEvidenceClient` owns only HTTP transport and wire-contract validation. It
does not import `finevidence`, rank documents, infer claims, or decide an
investment thesis. `HttpEvidenceProvider` adapts that client to the runtime's
`EvidenceProvider` protocol.

## Execution

For one `ResearchTask`, the adapter:

1. Builds a deterministic query from the case target/question and task title,
   purpose, and requirement descriptions.
2. Calls `POST /api/v1/evidence/search` with the target included in the query
   and a bounded `top_k`. It does not assume the external catalog has normalized
   entity metadata, so it avoids an exact entity filter that could hide valid
   evidence.
3. Sends the returned evidence IDs and typed requirement projections to
   `POST /api/v1/evidence/coverage`.
4. Resolves each returned evidence ID through
   `GET /api/v1/evidence/{id}/citation` and uses the citation response as the
   canonical source locator/provenance.
5. Emits runtime records. A record is `QUALIFIED` only when FinEvidence
   returns overall `ELIGIBLE` and marks that evidence `SUPPORTED`; otherwise it
   remains `NEEDS_REVIEW`.

The runtime may use stance fields for thesis presentation, but it must not
recompute external qualification. `HttpEvidenceProvider` declares external
qualification authority; the engine preserves the provider's qualification
result. Providers without that declaration retain the existing local
provenance and stance gate for backwards-compatible test providers.

## Wire models

The adapter validates the v1 response fields used by this repository with
Pydantic `extra="forbid"`. Unknown API versions, malformed evidence, missing
citation provenance, non-2xx responses, invalid JSON, and timeouts become
`EvidenceProviderError`; no synthetic fallback is created.

## Provenance

The runtime record keeps FinEvidence evidence ID, document ID, document name,
page, URL, document hash, table coordinates, verification status/confidence,
and a deterministic hash of the received evidence object. A generated locator
contains the page and available table coordinates. Visual evidence is kept as
metadata; the adapter never invents textual financial facts.
