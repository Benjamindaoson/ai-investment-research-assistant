from decimal import Decimal

from deepresearch.domain.models import FinancialSnapshot
from deepresearch.runtime.financial import FinancialAnalysisTool


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


def test_financial_analysis_preserves_negative_free_cash_flow() -> None:
    snapshot = FinancialSnapshot(period="Q1", revenue=Decimal("100"), operating_cash_flow=Decimal("-5"), capex=Decimal("10"))

    result = FinancialAnalysisTool().analyze(snapshot)

    assert result.free_cash_flow == Decimal("-15")
    assert result.fcf_margin_pct == Decimal("-15")


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
