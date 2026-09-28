import pytest
from pydantic import ValidationError

from hospitality_intelligence.metric_contracts import (
    MetricContract,
    load_metric_contracts,
)


def test_metric_contracts_are_unique_and_explicit() -> None:
    contracts = load_metric_contracts()
    ids = [metric.id for metric in contracts.metrics]

    assert len(ids) == len(set(ids))
    assert sum(metric.status == "implemented" for metric in contracts.metrics) >= 10
    assert all(metric.exclusions for metric in contracts.metrics)
    assert all(metric.limitations for metric in contracts.metrics)
    assert all(metric.reconciliation for metric in contracts.metrics)


def test_implemented_metric_requires_known_sources() -> None:
    payload = {
        "id": "bad_metric",
        "name": "Bad Metric",
        "domain": "rooms",
        "grain": "property_day",
        "formula": "a / b",
        "sources": ["unknown_fact"],
        "owner": "Revenue Management",
        "purpose": "Demonstrate contract source enforcement.",
        "exclusions": ["None"],
        "reconciliation": "Recompute the metric from governed sources.",
        "limitations": ["Synthetic test only."],
        "status": "implemented",
    }

    with pytest.raises(ValidationError):
        MetricContract.model_validate(payload)


def test_deferred_metric_may_have_unresolved_sources() -> None:
    contract = MetricContract.model_validate(
        {
            "id": "deferred_metric",
            "name": "Deferred Metric",
            "domain": "management",
            "grain": "period",
            "formula": "governed_future_formula",
            "sources": [],
            "owner": "General Management",
            "purpose": "Remain explicitly deferred until governance exists.",
            "exclusions": ["Not materialized."],
            "reconciliation": "Pending future governance and implementation.",
            "limitations": ["No current scoring credit."],
            "status": "deferred",
        }
    )

    assert contract.status == "deferred"
