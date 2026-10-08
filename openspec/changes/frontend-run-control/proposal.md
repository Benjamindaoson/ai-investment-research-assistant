# Frontend run control

## Why

The backend now has a durable cancellation path, but the frontend runtime
boundary cannot invoke it. A connected analyst workspace must be able to stop a
run through the same typed repository contract.

## What changes

- Add a typed runtime `cancelRun` service and repository method.
- Preserve explicit async errors and validate the returned run control state.

## Out of scope

- Wiring synthetic workspace controls to the backend in the same change.
- Client-side run state mutation outside TanStack Query.
