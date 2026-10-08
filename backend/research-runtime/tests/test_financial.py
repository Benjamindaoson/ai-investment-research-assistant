from decimal import Decimal

import pytest

from deepresearch.domain.models import FinancialFact, FinancialFactSet, FinancialSnapshot
from deepresearch.runtime.financial import FinancialAnalysisTool, financial_snapshot_from_facts


def test_financial_snapshot_is_mapped_only_from_explicit_typed_facts() -> None:
    fact_set = FinancialFactSet(
        period="FY2025",
        facts=[
            FinancialFact(
                field="revenue",
                value=Decimal("120"),
                period="FY2025",
                unit="GBP millions",
                currency="GBP",
                basis="REPORTED",
                evidence_ids=["evidence-revenue"],
            ),
            FinancialFact(
                field="prior_revenue",
                value=Decimal("100"),
                period="FY2025",
                unit="GBP millions",
                currency="GBP",
                basis="REPORTED",
                evidence_ids=["evidence-prior-revenue"],
            ),
        ],
    )

    snapshot, evidence_ids = financial_snapshot_from_facts(fact_set)

    assert snapshot == FinancialSnapshot(period="FY2025", revenue=Decimal("120"), prior_revenue=Decimal("100"))
    assert evidence_ids == {
        "revenue": ["evidence-revenue"],
        "prior_revenue": ["evidence-prior-revenue"],
    }


@pytest.mark.parametrize(
    ("facts", "message"),
    [
        (
            [
                FinancialFact(
                    field="gross_profit",
                    value=Decimal("1"),
                    period="FY2025",
                    unit="GBP millions",
                    currency="GBP",
                    basis="REPORTED",
                    evidence_ids=["evidence-1"],
                )
            ],
            "requires a revenue fact",
        ),
    ],
)
def test_financial_fact_set_rejects_incomplete_snapshot(facts: list[FinancialFact], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        FinancialFactSet(period="FY2025", facts=facts)


def test_financial_fact_set_rejects_duplicate_or_mixed_periods() -> None:
    revenue = FinancialFact(
        field="revenue",
        value=Decimal("120"),
        period="FY2025",
        unit="USD millions",
        currency="USD",
        basis="REPORTED",
        evidence_ids=["evidence-1"],
    )

    with pytest.raises(ValueError, match="fields must be unique"):
        FinancialFactSet(period="FY2025", facts=[revenue, revenue])
    with pytest.raises(ValueError, match="use the fact set period"):
        FinancialFactSet(
            period="FY2025",
            facts=[
                revenue,
                FinancialFact(
                    field="prior_revenue",
                    value=Decimal("100"),
                    period="FY2024",
                    unit="USD millions",
                    currency="USD",
                    basis="REPORTED",
                    evidence_ids=["evidence-2"],
                ),
            ],
        )


def test_financial_analysis_uses_decimal_math_and_hashes_inputs() -> None:
    snapshot = FinancialSnapshot(
        period="FY2025",
        revenue=Decimal("120"),
        prior_revenue=Decimal("100"),
        gross_profit=Decimal("60"),
        operating_income=Decimal("30"),
        operating_cash_flow=Decimal("35"),
        capex=Decimal("10"),
        cash=Decimal("50"),
        debt=Decimal("20"),
    )

    result = FinancialAnalysisTool().analyze(snapshot)

    assert result.revenue_growth_pct == Decimal("20.0")
    assert result.gross_margin_pct == Decimal("50.0")
    assert result.operating_margin_pct == Decimal("25.0")
    assert result.free_cash_flow == Decimal("25")
    assert result.fcf_margin_pct == Decimal("20.83333333333333333333333333")
    assert result.net_cash == Decimal("30")
    assert result.unavailable_metrics == []
    assert len(result.input_hash) == 64
    entries = {entry.metric: entry for entry in result.calculation_ledger}
    assert entries["revenue_growth_pct"].formula == "(revenue / prior_revenue - 1) × 100"
    assert entries["revenue_growth_pct"].inputs == {"revenue": Decimal("120"), "prior_revenue": Decimal("100")}
    assert entries["revenue_growth_pct"].value == result.revenue_growth_pct
    assert entries["revenue_growth_pct"].unit == "%"
    assert entries["revenue_growth_pct"].status == "AVAILABLE"


def test_financial_analysis_preserves_field_level_evidence_links() -> None:
    snapshot = FinancialSnapshot(period="FY2025", revenue=Decimal("100"))

    result = FinancialAnalysisTool().analyze(snapshot, {"revenue": ["evidence-1"]})

    assert result.evidence_ids == {"revenue": ["evidence-1"]}
    revenue_entry = next(entry for entry in result.calculation_ledger if entry.metric == "revenue_growth_pct")
    assert revenue_entry.evidence_ids == ["evidence-1"]
    assert result.snapshot == snapshot


def test_financial_analysis_preserves_negative_free_cash_flow() -> None:
    snapshot = FinancialSnapshot(period="Q1", revenue=Decimal("100"), operating_cash_flow=Decimal("-5"), capex=Decimal("10"))

    result = FinancialAnalysisTool().analyze(snapshot)

    assert result.free_cash_flow == Decimal("-15")
    assert result.fcf_margin_pct == Decimal("-15")
    entries = {entry.metric: entry for entry in result.calculation_ledger}
    assert entries["free_cash_flow"].status == "AVAILABLE"
    assert entries["free_cash_flow"].value == Decimal("-15")


def test_financial_analysis_marks_missing_and_zero_denominator_metrics() -> None:
    snapshot = FinancialSnapshot(period="FY2025", revenue=Decimal("0"), prior_revenue=Decimal("0"))

    result = FinancialAnalysisTool().analyze(snapshot)

    assert result.revenue_growth_pct is None
    assert result.gross_margin_pct is None
    assert result.operating_margin_pct is None
    assert result.free_cash_flow is None
    assert result.net_cash is None
    assert result.unavailable_metrics == [
        "revenue_growth_pct",
        "gross_margin_pct",
        "operating_margin_pct",
        "free_cash_flow",
        "fcf_margin_pct",
        "net_cash",
    ]
    assert len(result.calculation_ledger) == 6
    assert all(entry.status == "UNAVAILABLE" for entry in result.calculation_ledger)
    assert all(entry.value is None and entry.reason for entry in result.calculation_ledger)


def test_financial_calculation_ledger_is_stable_for_same_snapshot() -> None:
    snapshot = FinancialSnapshot(period="FY2025", revenue=Decimal("120.00"), prior_revenue=Decimal("100.00"))

    first = FinancialAnalysisTool().analyze(snapshot)
    second = FinancialAnalysisTool().analyze(snapshot)

    assert first.input_hash == second.input_hash
    assert first.calculation_ledger == second.calculation_ledger
