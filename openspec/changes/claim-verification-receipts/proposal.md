## Why

The runtime sends qualified claims to the external FinEvidence verification
endpoint, but the call is currently invisible inside the durable execution
record. A failed or unsupported verification therefore cannot be distinguished
from a synthesis-only outcome during replay or analyst review.

## What Changes

- Record a durable verification attempt before calling a provider's
  `verify_claim` operation.
- Persist whether the provider supported the claim, while distinguishing a
  successful negative result from transport or contract failure.
- Preserve lease ownership and UNKNOWN_EFFECT semantics across verification
  calls, just as for evidence collection.
- Surface verification receipts in the existing read-only tool trace.
- Add tests for supported, unsupported, failed, and lease-loss verification
  paths.

## Capabilities

### New Capabilities

- `claim-verification-receipts`: durable, auditable receipts for external claim
  verification operations.

### Modified Capabilities

None.

## Impact

- `backend/research-runtime/src/deepresearch/domain/models.py`
- `backend/research-runtime/src/deepresearch/runtime/engine.py`
- `apps/web/src/services/research-runtime-service.ts`
- `apps/web/src/components/runtime/runtime-tool-trace.tsx`
- Related backend and frontend tests and runtime documentation.

FinEvidence remains frozen and is accessed only through its existing HTTP
client boundary. No endpoint, retry policy, raw response storage, or new
dependency is introduced.
