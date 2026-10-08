# Branch consolidation — 2026-10-08

The repository owner requested merging every branch and retaining one branch.
`master` remains the default and retained development branch. This consolidation
preserves each original branch's commit history and independent additions.

## Original branch tips

| Branch | Tip before consolidation | Contribution |
| --- | --- | --- |
| `master` | `56b4ca469366200b94da3f266a3b840973f5477e` | Research-product and Financial Asset QA boundaries |
| `portfolio-readme-upgrade` | `903497ddfc2e3e245cb6917abe77e79c9f7ac485` | Atlas product explanation and workflow presentation |
| `main` | `c7307c8d47bbd4addd63933b0122a1f6336c4167` | Independent enterprise backend, Vite frontend, and design |
| `refactor/deepresearch-v2` | `e99611a9b4c24248f8fc34d38464828af6a0b901` | Current research runtime, connected UI, specs, and evaluation |

The consolidation commit uses the old `master` as its first parent and the
other three branch tips as additional parents. Updating `master` is therefore
a fast-forward. Deleting the redundant branch names does not remove any of
their commits from the retained branch's history.

## Content resolution

The DeepResearch tree is the implementation baseline. Changes on the other
branches were identified from their common ancestors, not by taking the union
of all historical file paths.

- Keep `apps/web`, `backend/research-runtime`, the root package and lockfiles,
  root Compose, and current product specifications from DeepResearch.
- Preserve all 63 `backend/enterprise-data-agent` files and all 84
  `frontend/data-ananlysis-demo` files from `main`, with original blob contents,
  executable modes, symbolic links, and binary assets.
- Keep the `main` design document at `DESIGN.md`, adding only a provenance and
  scope note. It describes the separate enterprise implementation.
- Resolve the README conflict around the current DeepResearch implementation,
  retaining Atlas's research-workflow explanation, product boundaries, and
  navigation to the enterprise projects. Retire statements that the current
  research runtime and persistence are only planned.
- Merge the ignore rules while retaining the `.env.example` exception and
  DeepResearch's runtime-state exclusions.
- Preserve DeepResearch's prior deletion of superseded pages and specifications.
  Files merely inherited by `main` from a common ancestor are not new changes
  to restore. Their original versions remain available in Git history.
- Mark the September branch-selection audit as historical, since its earlier
  exclusion of the enterprise projects was superseded by this user request.

## Runtime boundaries

Root JavaScript commands still select `web`; the pnpm workspace includes only
`apps/*`. The enterprise Vite frontend is not added to that workspace. Python
packages remain separate (`deepresearch` and `eiw`), with separate dependencies
and APIs. Root Compose remains the DeepResearch stack.

Run the enterprise backend from `backend/enterprise-data-agent`, because its
data and artifact defaults are relative to that directory. Its frontend must
use its own enterprise API, not the Research Runtime API. If running both
stacks at once, configure distinct ports: the enterprise API and FinEvidence
example both default to 8000, and both PostgreSQL Compose configurations map
host port 5432. This consolidation does not start or reconfigure those services.

## Historical documentation

The full original README versions remain available at immutable commits:

- [Original master README](https://github.com/Benjamindaoson/ai-investment-research-assistant/blob/56b4ca469366200b94da3f266a3b840973f5477e/README.md)
- [Atlas portfolio README](https://github.com/Benjamindaoson/ai-investment-research-assistant/blob/903497ddfc2e3e245cb6917abe77e79c9f7ac485/README.md)
- [Enterprise workspace README](https://github.com/Benjamindaoson/ai-investment-research-assistant/blob/c7307c8d47bbd4addd63933b0122a1f6336c4167/README.md)
- [DeepResearch README](https://github.com/Benjamindaoson/ai-investment-research-assistant/blob/e99611a9b4c24248f8fc34d38464828af6a0b901/README.md)

These historical documents describe their original snapshots. Current setup
and ownership are documented in the root README and the respective module
READMEs.

## Validation scope

Checks performed on the consolidated worktree with the original dependency
lockfiles and pnpm 11.9.0:

| Check | Result |
| --- | --- |
| Frozen-lockfile dependency installation | Passed; lockfiles unchanged |
| Frontend lint and TypeScript | Passed |
| Frontend unit/component suite | 27 test files, 103 tests passed |
| Next.js production build | Passed |
| Research Runtime offline suite | 146 passed; 4 integration tests deselected |
| Enterprise project content and modes vs. original `main` | Identical across all 147 files |
| DeepResearch code and default configuration vs. original branch | Unchanged |

The four deselected backend tests require FinEvidence (two tests), PostgreSQL,
or Redis. Browser E2E and real-provider integration were not run for this
consolidation. Independent enterprise projects were preserved byte-for-byte;
their own application tests were not rerun.

Validation targets the consolidated tree: unchanged DeepResearch application
blobs, unchanged enterprise project blobs and Git modes, preserved default
entry points, ignore-rule behavior, and available automated project checks.
Provider-backed tests require separately configured external services. No
claim is made that branch consolidation resolves pre-existing runtime or
research-quality issues.
