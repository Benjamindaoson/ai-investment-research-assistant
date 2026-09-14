"""Deterministic financial calculations over caller-supplied snapshots."""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256

from deepresearch.domain.models import (
    CalculationLedgerEntry,
    FinancialAnalysisResult,
    FinancialSnapshot,
    ScenarioAssumption,
    ScenarioValuationInput,
    ScenarioValuationResult,
    ValuationScenariosResult,
)


class FinancialAnalysisTool:
    """Compute transparent metrics without fetching or inventing financial data."""

    def analyze(self, snapshot: FinancialSnapshot, evidence_ids: dict[str, list[str]] | None = None) -> FinancialAnalysisResult:
        input_hash = sha256(snapshot.model_dump_json().encode()).hexdigest()
        revenue_growth = self._growth(snapshot.revenue, snapshot.prior_revenue)
        gross_margin = self._ratio(snapshot.gross_profit, snapshot.revenue)
        operating_margin = self._ratio(snapshot.operating_income, snapshot.revenue)
        free_cash_flow = None
        if snapshot.operating_cash_flow is not None and snapshot.capex is not None:
            free_cash_flow = snapshot.operating_cash_flow - snapshot.capex
        fcf_margin = self._ratio(free_cash_flow, snapshot.revenue)
        net_cash = None
        if snapshot.cash is not None and snapshot.debt is not None:
            net_cash = snapshot.cash - snapshot.debt

        links = evidence_ids or {}
        ledger = [
            self._entry(
                "revenue_growth_pct",
                "(revenue / prior_revenue - 1) × 100",
                {"revenue": snapshot.revenue, **({"prior_revenue": snapshot.prior_revenue} if snapshot.prior_revenue is not None else {})},
                revenue_growth,
                "%",
                self._linked_ids(links, "revenue", "prior_revenue"),
                "prior_revenue is required and must be non-zero" if revenue_growth is None else None,
            ),
            self._entry(
                "gross_margin_pct",
                "gross_profit / revenue × 100",
                {"gross_profit": snapshot.gross_profit, "revenue": snapshot.revenue} if snapshot.gross_profit is not None else {"revenue": snapshot.revenue},
                gross_margin,
                "%",
                self._linked_ids(links, "gross_profit", "revenue"),
                "gross_profit is required and revenue must be non-zero" if gross_margin is None else None,
            ),
            self._entry(
                "operating_margin_pct",
                "operating_income / revenue × 100",
                {"operating_income": snapshot.operating_income, "revenue": snapshot.revenue} if snapshot.operating_income is not None else {"revenue": snapshot.revenue},
                operating_margin,
                "%",
                self._linked_ids(links, "operating_income", "revenue"),
                "operating_income is required and revenue must be non-zero" if operating_margin is None else None,
            ),
            self._entry(
                "free_cash_flow",
                "operating_cash_flow - capex",
                {key: value for key, value in {"operating_cash_flow": snapshot.operating_cash_flow, "capex": snapshot.capex}.items() if value is not None},
                free_cash_flow,
                "currency",
                self._linked_ids(links, "operating_cash_flow", "capex"),
                "operating_cash_flow and capex are required" if free_cash_flow is None else None,
            ),
            self._entry(
                "fcf_margin_pct",
                "free_cash_flow / revenue × 100",
                {"free_cash_flow": free_cash_flow, "revenue": snapshot.revenue} if free_cash_flow is not None else {"revenue": snapshot.revenue},
                fcf_margin,
                "%",
                self._linked_ids(links, "operating_cash_flow", "capex", "revenue"),
                "free_cash_flow is required and revenue must be non-zero" if fcf_margin is None else None,
            ),
            self._entry(
                "net_cash",
                "cash - debt",
                {key: value for key, value in {"cash": snapshot.cash, "debt": snapshot.debt}.items() if value is not None},
                net_cash,
                "currency",
                self._linked_ids(links, "cash", "debt"),
                "cash and debt are required" if net_cash is None else None,
            ),
        ]

        return FinancialAnalysisResult(
            period=snapshot.period,
            snapshot=snapshot,
            input_hash=input_hash,
            revenue_growth_pct=revenue_growth,
            gross_margin_pct=gross_margin,
            operating_margin_pct=operating_margin,
            free_cash_flow=free_cash_flow,
            fcf_margin_pct=fcf_margin,
            net_cash=net_cash,
            unavailable_metrics=[entry.metric for entry in ledger if entry.status == "UNAVAILABLE"],
            evidence_ids=links,
            calculation_ledger=ledger,
        )

    @staticmethod
    def _entry(
        metric: str,
        formula: str,
        inputs: dict[str, Decimal],
        value: Decimal | None,
        unit: str,
        evidence_ids: list[str],
        reason: str | None,
    ) -> CalculationLedgerEntry:
        return CalculationLedgerEntry(
            metric=metric,
            formula=formula,
            inputs=inputs,
            value=value,
            unit=unit,
            status="AVAILABLE" if value is not None else "UNAVAILABLE",
            reason=reason,
            evidence_ids=evidence_ids,
        )

    @staticmethod
    def _linked_ids(links: dict[str, list[str]], *fields: str) -> list[str]:
        return list(dict.fromkeys(evidence_id for field in fields for evidence_id in links.get(field, [])))

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


class ScenarioValuationTool:
    """Calculate an illustrative, explicit terminal-value scenario bridge."""

    def analyze(self, run_id: str, case_id: str, request: ScenarioValuationInput) -> ValuationScenariosResult:
        input_hash = sha256(request.model_dump_json().encode()).hexdigest()
        results = [self._scenario(request.base_revenue, scenario) for scenario in request.scenarios]
        return ValuationScenariosResult(
            run_id=run_id,
            case_id=case_id,
            input_hash=input_hash,
            base_revenue=request.base_revenue,
            base_revenue_evidence_ids=request.base_revenue_evidence_ids,
            scenarios=results,
            provenance={
                "calculator": "decimal-terminal-value-bridge",
                "formula_version": "v1",
                "illustrative": True,
            },
        )

    @staticmethod
    def _scenario(base_revenue: Decimal, assumptions: ScenarioAssumption) -> ScenarioValuationResult:
        rate_spread = assumptions.discount_rate_pct - assumptions.terminal_growth_pct
        if rate_spread <= 0:
            raise ValueError(f"{assumptions.name} discount rate must exceed terminal growth")
        projected_revenue = base_revenue * (Decimal("1") + assumptions.revenue_growth_pct / Decimal("100"))
        projected_operating_income = projected_revenue * assumptions.operating_margin_pct / Decimal("100")
        free_cash_flow = projected_revenue * assumptions.fcf_margin_pct / Decimal("100")
        terminal_value = free_cash_flow * Decimal("100") / rate_spread
        equity_value = terminal_value + assumptions.net_cash
        value_per_share = equity_value / assumptions.shares_outstanding
        return ScenarioValuationResult(
            scenario=assumptions.name,
            assumptions=assumptions,
            projected_revenue=projected_revenue,
            projected_operating_income=projected_operating_income,
            free_cash_flow=free_cash_flow,
            terminal_value=terminal_value,
            equity_value=equity_value,
            value_per_share=value_per_share,
        )
