# Design

`InvestmentMemo` is persisted inside the existing run payload so local
checkpoint/resume and read-back retain one source of truth. It is a projection,
not a second state machine: execution creates a `DRAFT` for partial runs and a
`READY_FOR_REVIEW` memo for fully qualified runs. Human approval of the thesis
is the only write path to `APPROVED`.

The memo stores claim IDs, qualified evidence IDs, qualified counter/conflicting
evidence IDs, and unresolved requirement IDs. Its executive summary is a
deterministic count-based statement; it never invents financial facts or
citations. Rich writing can be added later behind the same evidence and review
boundary.
