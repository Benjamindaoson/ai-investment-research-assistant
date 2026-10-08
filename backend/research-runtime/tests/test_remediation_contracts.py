from decimal import Decimal

import pytest

from deepresearch.domain.models import FinancialFact, FinancialFactSet
from deepresearch.runtime.evidence import HttpEvidenceProvider


def _fact(field: str, value: str, *, currency: str = "USD", unit: str = "USD millions") -> FinancialFact:
    return FinancialFact(
        field=field,
        value=Decimal(value),
        period="FY2025",
        unit=unit,
        currency=currency,
        basis="REPORTED",
        evidence_ids=[f"evidence-{field}"],
    )


def test_financial_fact_set_rejects_mixed_currencies_and_unit_scales() -> None:
    with pytest.raises(ValueError, match="one currency"):
        FinancialFactSet(
            period="FY2025",
            facts=[
                _fact("revenue", "120", currency="USD"),
                _fact("gross_profit", "60", currency="EUR"),
            ],
        )

    with pytest.raises(ValueError, match="one unit scale"):
        FinancialFactSet(
            period="FY2025",
            facts=[
                _fact("revenue", "120", unit="USD millions"),
                _fact("gross_profit", "60", unit="USD billions"),
            ],
        )


def test_financial_fact_set_accepts_equivalent_unit_spellings() -> None:
    fact_set = FinancialFactSet(
        period="FY2025",
        facts=[
            _fact("revenue", "120", unit="USD millions"),
            _fact("gross_profit", "60", unit="USD mm"),
        ],
    )

    assert [fact.field for fact in fact_set.facts] == ["revenue", "gross_profit"]


def test_finevidence_verification_uses_provider_evidence_id_candidates() -> None:
    assert HttpEvidenceProvider._canonical_evidence_ids(["ev-1:risk-signal"]) == [
        "ev-1:risk-signal",
        "ev-1",
    ]
    assert HttpEvidenceProvider._canonical_evidence_ids(["hsbc-fy2025-annual-report:p365:page"]) == [
        "hsbc-fy2025-annual-report:p365:page"
    ]
    assert HttpEvidenceProvider._canonical_evidence_ids(["doc:p365:page:risk-signal"]) == [
        "doc:p365:page:risk-signal",
        "doc:p365:page",
    ]
