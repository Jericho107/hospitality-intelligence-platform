"""Validate source and metric contracts before analytical implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


class SourceContract(BaseModel):
    """Contract for one synthetic operational source."""

    id: str = Field(min_length=1)
    system: str = Field(min_length=1)
    grain: str = Field(min_length=1)
    primary_key: list[str] = Field(min_length=1)
    required_fields: list[str] = Field(min_length=1)
    time_field: str = Field(min_length=1)
    financial_fields: list[str] = Field(default_factory=list)
    pii_allowed: bool

    @model_validator(mode="after")
    def validate_field_references(self) -> "SourceContract":
        required = set(self.required_fields)
        missing_pk = set(self.primary_key) - required
        if missing_pk:
            raise ValueError(f"{self.id}: primary-key fields missing from required_fields: {missing_pk}")
        if self.time_field not in required:
            raise ValueError(f"{self.id}: time_field must be required")
        missing_financial = set(self.financial_fields) - required
        if missing_financial:
            raise ValueError(
                f"{self.id}: financial fields missing from required_fields: {missing_financial}"
            )
        return self


class MetricContract(BaseModel):
    """Governance contract for one management metric."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    domain: Literal["rooms", "fnb", "purchasing", "inventory", "labour", "planning"]
    purpose: str = Field(min_length=10)
    formula: str = Field(min_length=3)
    grain: str = Field(min_length=1)
    sources: list[str] = Field(min_length=1)
    owner: str = Field(min_length=1)
    refresh: str = Field(min_length=1)
    exclusions: list[str] = Field(min_length=1)
    reconciliation: str = Field(min_length=10)
    limitations: list[str] = Field(min_length=1)


class SourceContractFile(BaseModel):
    """Container for source contracts."""

    sources: list[SourceContract] = Field(min_length=1)


class MetricContractFile(BaseModel):
    """Container for metric contracts."""

    metrics: list[MetricContract] = Field(min_length=1)


def _load_yaml(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected mapping at document root")
    return payload


def _assert_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label} detected")


def load_source_contracts() -> SourceContractFile:
    """Load and validate operational source contracts."""

    result = SourceContractFile.model_validate(_load_yaml(CONFIG_DIR / "source_contracts.yml"))
    _assert_unique([source.id for source in result.sources], "source id")
    return result


def load_metric_contracts(
    sources: SourceContractFile | None = None,
) -> MetricContractFile:
    """Load metrics and ensure every declared source exists."""

    source_contracts = sources or load_source_contracts()
    source_ids = {source.id for source in source_contracts.sources}
    result = MetricContractFile.model_validate(_load_yaml(CONFIG_DIR / "metric_contracts.yml"))
    _assert_unique([metric.id for metric in result.metrics], "metric id")

    for metric in result.metrics:
        unknown = set(metric.sources) - source_ids
        if unknown:
            raise ValueError(f"{metric.id}: unknown source contracts: {sorted(unknown)}")

    return result


def validate_contracts() -> tuple[SourceContractFile, MetricContractFile]:
    """Validate the complete governance contract layer."""

    sources = load_source_contracts()
    metrics = load_metric_contracts(sources)
    return sources, metrics


def main() -> None:
    """CLI entry point."""

    sources, metrics = validate_contracts()
    print(f"Validated {len(sources.sources)} source contracts.")
    print(f"Validated {len(metrics.metrics)} metric contracts.")


if __name__ == "__main__":
    main()
