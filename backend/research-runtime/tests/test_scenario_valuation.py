from decimal import Decimal
from hashlib import sha256

import pytest

from deepresearch.domain.models import (
    ResearchCase,
    ResearchRun,
    ScenarioAssumption,
    ScenarioValuationInput,
)
from deepresearch.persistence.store import SQLiteStore
from deepresearch.runtime.engine import ResearchEngine
from deepresearch.runtime.evidence import DeterministicEvidenceProvider
from deepresearch.runtime.financial import ScenarioValuationTool


def scenario(name: str, evidence_id: str) -> ScenarioAssumption:
    links = {
        "revenue_growth_pct": [evidence_id],
        "operating_margin_pct": [evidence_id],
        "fcf_margin_pct": [evidence_id],
        "discount_rate_pct": [evidence_id],
        "terminal_growth_pct": [evidence_id],
        "net_cash": [evidence_id],
        "shares_outstanding": [evidence_id],
    }
    return ScenarioAssumption(
        name=name,
        revenue_growth_pct={"BULL": "20", "BASE": "10", "BEAR": "-10"}[name],
        operating_margin_pct={"BULL": "30", "BASE": "25", "BEAR": "15"}[name],
        fcf_margin_pct={"BULL": "25", "BASE": "20", "BEAR": "10"}[name],
        discount_rate_pct={"BULL": "10", "BASE": "11", "BEAR": "13"}[name],
        terminal_growth_pct={"BULL": "3", "BASE": "2", "BEAR": "0"}[name],
        net_cash="10",
        shares_outstanding="10",
        evidence_ids=links,
    )


def request(evidence_id: str) -> ScenarioValuationInput:
    return ScenarioValuationInput(
        base_revenue="100",
        base_revenue_evidence_ids=[evidence_id],
        scenarios=[scenario(name, evidence_id) for name in ("BULL", "BASE", "BEAR")],
    )


def test_scenario_tool_calculates_explicit_decimal_outputs() -> None:
    input_data = request("ev-1")
    result = ScenarioValuationTool().analyze("run-1", "case-1", input_data)
    bull = result.scenarios[0]

    assert result.input_hash == sha256(input_data.model_dump_json().encode()).hexdigest()
    assert bull.scenario == "BULL"
    assert bull.projected_revenue == Decimal("120")
    assert bull.projected_operating_income == Decimal("36")
    assert bull.free_cash_flow == Decimal("30")
    assert bull.terminal_value == Decimal("428.5714285714285714285714286")
    assert bull.equity_value == Decimal("438.5714285714285714285714286")
    assert bull.value_per_share == Decimal("43.85714285714285714285714286")


def test_engine_persists_only_qualified_scenario_evidence(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "runtime.sqlite3")
    engine = ResearchEngine(store, DeterministicEvidenceProvider())
    run = engine.create_run(
        ResearchCase(id="case-scenarios", question="Assess ACME valuation", target="ACME"),
    )
    completed = engine.execute(run.id)
    evidence_id = next(item.id for item in completed.evidence if item.qualification == "QUALIFIED")
    artifact = ScenarioValuationTool().analyze(run.id, run.case_id, request(evidence_id))

    recorded = engine.record_valuation_scenarios(run.id, artifact)
    reloaded = ResearchRun.model_validate(store.get_run(run.id))

    assert recorded.valuation_scenarios is not None
    assert reloaded.valuation_scenarios is not None
    assert reloaded.valuation_scenarios.input_hash == artifact.input_hash
    assert any(event["event_type"] == "VALUATION_SCENARIOS_RECORDED" for event in store.events(run.id))

    unqualified = completed.evidence[0].model_copy(update={"qualification": "NEEDS_REVIEW"})
    store.save_run(completed.model_copy(update={"evidence": [unqualified, *completed.evidence[1:]]}).model_dump(mode="json"))
    with pytest.raises(ValueError, match="not qualified"):
        engine.record_valuation_scenarios(run.id, artifact)


def test_scenario_input_rejects_invalid_rate_spread() -> None:
    with pytest.raises(ValueError, match="discount rate must exceed terminal growth"):
        bad = request("ev-1").model_copy(
            update={"scenarios": [scenario(name, "ev-1") for name in ("BULL", "BASE", "BEAR")]}
        )
        bad.scenarios[0].discount_rate_pct = Decimal("3")
        bad.scenarios[0].terminal_growth_pct = Decimal("3")
        ScenarioValuationTool().analyze("run-1", "case-1", bad)
