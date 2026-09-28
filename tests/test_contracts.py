from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from hospitality_intelligence.contracts import (
    MetricContractFile,
    SourceContractFile,
    load_metric_contracts,
    load_source_contracts,
)


def test_source_contracts_are_valid_and_unique() -> None:
    contracts = load_source_contracts()
    ids = [source.id for source in contracts.sources]

    assert len(ids) == len(set(ids))
    assert len(ids) == 6
    assert all(source.pii_allowed is False for source in contracts.sources)


def test_metric_contracts_are_valid_and_reference_known_sources() -> None:
    sources = load_source_contracts()
    metrics = load_metric_contracts(sources)
    source_ids = {source.id for source in sources.sources}

    assert len(metrics.metrics) >= 10
    assert all(set(metric.sources).issubset(source_ids) for metric in metrics.metrics)
    assert all(metric.limitations for metric in metrics.metrics)
    assert all(metric.reconciliation for metric in metrics.metrics)


def test_source_primary_key_must_be_required() -> None:
    payload = {
        "sources": [
            {
                "id": "broken",
                "system": "Synthetic",
                "grain": "row",
                "primary_key": ["missing_id"],
                "required_fields": ["value"],
                "time_field": "value",
                "financial_fields": [],
                "pii_allowed": False,
            }
        ]
    }

    with pytest.raises(ValidationError):
        SourceContractFile.model_validate(payload)


def test_metric_contract_requires_limitations() -> None:
    payload = {
        "metrics": [
            {
                "id": "metric",
                "name": "Metric",
                "domain": "rooms",
                "purpose": "Support a real management decision.",
                "formula": "a / b",
                "grain": "date",
                "sources": ["pms_room_nights"],
                "owner": "Operations",
                "refresh": "daily",
                "exclusions": ["None"],
                "reconciliation": "Reconcile numerator and denominator to source.",
                "limitations": [],
            }
        ]
    }

    with pytest.raises(ValidationError):
        MetricContractFile.model_validate(payload)


def test_yaml_files_are_parseable() -> None:
    root = Path(__file__).resolve().parents[1]
    for path in (root / "config").glob("*.yml"):
        assert isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict)
