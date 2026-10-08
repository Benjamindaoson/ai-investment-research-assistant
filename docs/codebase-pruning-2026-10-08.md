# Codebase pruning and modernization log — 2026-10-08

The active repository scope is now **Financial DeepResearch**.

Cleaned in this pass:

- Removed the historical enterprise-workspace `DESIGN.md` snapshot.
- Rewrote the root README around the active Financial DeepResearch product.
- Marked historical branch-consolidation and independent-project assets as non-active in current documentation.

Not yet physically removed in this pass:

- `backend/enterprise-data-agent`
- `frontend/data-ananlysis-demo`
- generated historical evaluation reports

Those directories are still present in Git because GitHub's safety guard rejected the large tree-deletion operation through the connector. They should be deleted in a follow-up commit using a local git checkout or a repository-maintenance PR that removes those paths in one reviewed diff.

Active ownership after pruning:

- `apps/web`: Financial DeepResearch analyst workspace.
- `backend/research-runtime`: durable research runtime, evidence boundary, memo/review/decision workflow.
- `docs/product` and `openspec`: current product and change specifications.

Next modernization targets:

1. cancellation and in-flight worker race handling;
2. replanning invalidation when task contracts change;
3. VERIFYING-stage recovery;
4. atomic run/event/memory writes;
5. fact-level numeric verification against source evidence;
6. CI for backend, frontend, and key runtime regressions.
