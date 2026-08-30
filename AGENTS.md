# Autonomous Execution Policy

For implementation tasks, continue autonomously until the requested task is complete.

Do not ask for:
- permission to continue
- approval of routine implementation decisions
- confirmation after intermediate steps
- confirmation before running normal tests, lint, typecheck, build, or local development commands

When requirements are underspecified:
- inspect the existing code, OpenSpec artifacts, tests, design references, and repository conventions
- make the most reasonable assumption consistent with the existing product direction
- continue implementation

Do not stop after planning. Implement the plan.

After making changes:
- run relevant lint
- run strict typecheck
- run tests
- run production build when appropriate
- fix failures caused by the changes
- update relevant OpenSpec tasks only when actually completed

Only stop and ask the user when:
1. a required secret, credential, or external input is unavailable;
2. two choices would materially change product behavior and existing specifications do not resolve the choice;
3. the requested action is irreversible or destructive outside this repository;
4. an external blocker makes further progress impossible.

Do not ask "should I continue?".
Continue until complete or genuinely blocked.

At completion, report:
- what was implemented
- validation performed
- remaining blockers or tasks