# Design

`POST /research-cases` remains the single creation transaction from the API's
perspective. `PlannerProviderError` is a dependency-availability failure and
returns 503; `ValueError` from canonical plan validation returns 422. The
engine is called before any case/run is persisted, so both failures leave no
partial run.
