# Frontend live run workspace

## Why

The canonical backend run is executable, but the Next.js app currently only
renders synthetic case workspaces. A connected analyst needs one narrow screen
that can create, start, inspect, and cancel a real runtime run.

## What changes

- Add typed runtime create/get/execute contracts and repository methods.
- Add a `/runtime/[runId]` workspace for run state, tasks, evidence coverage,
  memo status, and cancellation.
- Add configurable local CORS to the backend so the browser can call the
  runtime explicitly.

## Out of scope

- Replacing every synthetic route in this phase.
- Mapping the existing frontend-only plan editor into backend task contracts;
  that requires an explicit product contract for user-authored task plans.
