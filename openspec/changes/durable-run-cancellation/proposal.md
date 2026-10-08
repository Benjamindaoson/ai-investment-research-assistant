# Durable run cancellation

## Why

`ResearchRun` already models `CANCELLED`, but the runtime has no explicit
control path to set it. A durable research system must let an analyst stop a
run and read back that decision without later execution silently continuing.

## What changes

- Add an idempotent engine cancellation method with an append-only event.
- Expose a cancellation endpoint.
- Make tests prove cancelled runs do not collect more evidence or synthesize a
  completed memo.

## Out of scope

- Interrupting an already executing external HTTP request.
- Distributed cancellation leases or worker orchestration.
