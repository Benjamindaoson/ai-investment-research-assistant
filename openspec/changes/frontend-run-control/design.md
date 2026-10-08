# Design

The HTTP service posts a validated cancellation reason and parses the returned
run ID, case ID, and terminal state. The full backend run remains available via
the run endpoint; this narrow contract prevents the control action from
duplicating the domain model in the frontend.
