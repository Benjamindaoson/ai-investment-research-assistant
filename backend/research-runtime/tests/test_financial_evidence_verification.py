from decimal import Decimal

import pytest

from deepresearch.domain.models import EvidenceRecord, FinancialFact, FinancialFactSet
from deepresearch.runtime.financial import validate_financial_fact_evidence


def _evidence(excerpt: str, *, evidence_id: str = "evidence-1", fixture: bool = False) -> EvidenceRecord:
    return EvidenceRecord(
        id=evidence_id,
        task_id="task-1",
        requirement_id="req-1",
        stance="SUPPORTING",
        qualification="QUALIFIED",
        source_id="source-1",
        source_title="ACME filing",
        excerpt=excerpt,
        provider="unit-test",
        provenance={"fixture": fixture},
    )


def _fact(value: str = "120", evidence_id: str = "evidence-1") -> FinancialFact:
    return FinancialFact(
        field="revenue",
        value=Decimal(value),
        period="FY2025",
        unit="USD mm",
        currency="USD",
        basis="REPORTED",
        evidence_ids=[evidence_id],
    )


def test_financial_fact_text_verification_accepts_bound_value_period_unit_currency() -> None:
    fact_set = FinancialFactSet(period="FY2025", facts=[_fact()])
    evidence = [
        _evidence("ACME FY2025 revenue was 120 USD mm in the reported period."),
    ]

    validate_financial_fact_evidence(fact_set, evidence)


def test_financial_fact_text_verification_rejects_mismatched_value() -> None:
    fact_set = FinancialFactSet(period="FY2025", facts=[_fact("999")])
    evidence = [
        _evidence("ACME FY2025 revenue was 120 USD mm in the reported period."),
    ]

    with pytest.raises(ValueError, match="not supported by linked evidence text"):
        validate_financial_fact_evidence(fact_set, evidence)


def test_financial_fact_text_verification_rejects_mismatched_period() -> None:
    fact_set = FinancialFactSet(period="FY2025", facts=[_fact()])
    evidence = [
        _evidence("ACME FY2024 revenue was 120 USD mm in the reported period."),
    ]

    with pytest.raises(ValueError, match="not supported by linked evidence text"):
        validate_financial_fact_evidence(fact_set, evidence)


def test_financial_fact_text_verification_rejects_missing_evidence_id() -> None:
    fact_set = FinancialFactSet(period="FY2025", facts=[_fact(evidence_id="missing")])
    evidence = [
        _evidence("ACME FY2025 revenue was 120 USD mm in the reported period."),
    ]

    with pytest.raises(ValueError, match="financial evidence not found"):
        validate_financial_fact_evidence(fact_set, evidence)
