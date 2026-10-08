## 1. Query refresh policy

- [x] 1.1 Add a terminal-state-aware refresh interval helper and apply it to
  run and trace queries.
- [x] 1.2 Add hook tests for active and terminal refresh decisions.

## 2. Cache coherence and reviewer feedback

- [x] 2.1 Invalidate trace and case history after execute, replan, and cancel;
  show a live-refresh indicator for non-terminal runs.
- [x] 2.2 Run frontend tests, lint, typecheck, build, OpenSpec, CodeGraph,
  runtime smoke, and Git checks.
