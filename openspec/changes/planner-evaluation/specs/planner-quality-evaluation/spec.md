## ADDED Requirements

### Requirement: Planner quality is evaluated independently from execution

The repository SHALL provide an executable planner scorer that evaluates a `ResearchPlan` against an independently authored golden case without executing tools or relying on model self-reported quality.

#### Scenario: Deterministic plan passes the golden case

- **WHEN** the deterministic planner produces a plan for the golden financial research case
- **THEN** the planner evaluation reports PASS for required task coverage, dependency edges, evidence requirements, counter-evidence coverage, and task ceiling

#### Scenario: Planner evaluation does not call evidence tools

- **WHEN** `score_plan` evaluates a plan
- **THEN** it uses only the plan and golden case inputs and does not invoke an evidence provider or mutate durable runtime state

### Requirement: Planner checks expose actionable failures

The planner scorer SHALL return named checks with observed values and expected values for missing tasks, unexpected dependency edges, missing evidence requirements, missing counter-evidence, and duplicate or excessive tasks.

#### Scenario: Missing coverage fails explicitly

- **WHEN** a plan omits a required task ID
- **THEN** the result is `passed=false` and the task coverage check names the missing task ID

#### Scenario: Missing counter-evidence fails explicitly

- **WHEN** a plan contains no task requiring a `COUNTER` evidence stance where the golden case requires one
- **THEN** the counter-evidence check is `FAIL` and the result does not claim planner quality passed

### Requirement: Evaluation output keeps plan and run facts separate

The executable evaluation command SHALL report planner evaluation and runtime execution evaluation as separate results.

#### Scenario: Plan passes while run is partial

- **WHEN** a structurally valid plan is executed with incomplete evidence
- **THEN** the output can report a passing plan evaluation and a partial or failed run evaluation without conflating the two
