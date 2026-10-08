# API error boundaries

## Why

Planner provider failures are currently safe from persistence but are not
translated into a stable HTTP contract. Clients need to distinguish an
unavailable provider from an invalid research request.

## What changes

- Translate planner provider failures during case creation to HTTP 503.
- Translate plan validation failures to HTTP 422.
- Preserve the no-partial-run invariant and test both paths.

## Out of scope

- A generalized error envelope for every future endpoint.
- Automatic retries or provider fallback.
