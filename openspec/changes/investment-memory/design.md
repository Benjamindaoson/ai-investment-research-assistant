# Design

`InvestmentMemory` is a target-level projection stored in a dedicated SQLite
row. Each completed or partial run appends its case, run, memo, and thesis IDs;
the previous latest thesis is retained as a version reference. The latest
unresolved requirement IDs and decision IDs are read directly from the newest
run/decision update.

The projection stores references, not copied evidence or free-form chat. The
run payload remains the source of truth for evidence, claims, thesis, and memo;
memory is a compact index for subsequent research planning.
