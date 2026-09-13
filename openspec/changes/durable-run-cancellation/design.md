# Design

Cancellation is a terminal run state. The engine persists `completed_at`, the
cancelled state, and a `RUN_CANCELLED` event. Calling cancel again is idempotent
and returns the existing terminal run. `execute()` already treats terminal
states as read-only, so a cancelled run cannot collect more evidence or create
a completion synthesis.

The current local engine cannot abort a provider call already in progress; the
API contract records cancellation once control returns. A future worker runtime
can add cancellation tokens behind this same boundary.
