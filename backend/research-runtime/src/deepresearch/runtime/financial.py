"""Deterministic financial calculations over caller-supplied snapshots."""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256

from deepresearch.domain.models import FinancialAnalysisResult, FinancialSnapshot


class FinancialAnalysisTool:
    """Compute transparent metrics without fetching or inventing financial data."""

    def analyze(self, snapshot: FinancialSnapshot) -> FinancialAnalysisResult:
        input_hash = sha256(snapshot.model_dump_json().encode()).hexdigest()
        unavailable: list[str] = []

        revenue_growth = self._growth(snapshot.revenue, snapshot.prior_revenue)
        if revenue_growth is None:
            unavailable.append("revenue_growth_pct")

        gross_margin = self._ratio(snapshot.gross_profit, snapshot.revenue)
        if gross_margin is None:
            unavailable.append("gross_margin_pct")

        operating_margin = self._ratio(snapshot.operating_income, snapshot.revenue)
        if operating_margin is None:
            unavailable.append("operating_margin_pct")

        free_cash_flow = None
        if snapshot.operating_cash_flow is not None and snapshot.capex is not None:
            free_cash_flow = snapshot.operating_cash_flow - snapshot.capex
        else:
            unavailable.append("free_cash_flow")

        fcf_margin = self._ratio(free_cash_flow, snapshot.revenue)
        if fcf_margin is None:
            unavailable.append("fcf_margin_pct")

        net_cash = None
        if snapshot.cash is not None and snapshot.debt is not None:
            net_cash = snapshot.cash - snapshot.debt
        else:
            unavailable.append("net_cash")

        return FinancialAnalysisResult(
            period=snapshot.period,
            input_hash=input_hash,
            revenue_growth_pct=revenue_growth,
            gross_margin_pct=gross_margin,
            operating_margin_pct=operating_margin,
            free_cash_flow=free_cash_flow,
            fcf_margin_pct=fcf_margin,
            net_cash=net_cash,
            unavailable_metrics=unavailable,
        )

    @staticmethod
    def _ratio(numerator: Decimal | None, denominator: Decimal) -> Decimal | None:
        if numerator is None or denominator == 0:
            return None
        return numerator / denominator * 100

    @staticmethod
    def _growth(current: Decimal, prior: Decimal | None) -> Decimal | None:
        if prior is None or prior == 0:
            return None
        return (current / prior - 1) * 100
