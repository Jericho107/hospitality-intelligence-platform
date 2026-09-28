"""Machine-readable governance for hospitality KPI definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "config" / "metric_contracts.yml"

IMPLEMENTED_MART_SOURCES = {
    "fact_room_inventory_daily",
    "fact_room_bookings_daily",
    "fact_pos_outlet_daily",
    "fact_purchases_daily",
    "dim_product",
    "fact_inventory_daily",
    "fact_labour_daily",
}


class MetricContract(BaseModel):
    """One governed KPI definition."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    domain: Literal["rooms", "fnb", "purchasing", "inventory", "labour", "management"]
    grain: str = Field(min_length=1)
    formula: str = Field(min_length=3)
    sources: list[str]
    owner: str = Field(min_length=1)
    purpose: str = Field(min_length=10)
    exclusions: list[str] = Field(min_length=1)
    reconciliation: str = Field(min_length=10)
    limitations: list[str] = Field(min_length=1)
    status: Literal["implemented", "deferred"]

    @model_validator(mode="after")
    def validate_status_boundary(self) -> "MetricContract":
        if self.status == "implemented":
            if not self.sources:
                raise ValueError(f"{self.id}: implemented metric must declare sources")
            unknown = set(self.sources) - IMPLEMENTED_MART_SOURCES
            if unknown:
                raise ValueError(
                    f"{self.id}: implemented metric references unknown sources: {sorted(unknown)}"
                )
        return self


class MetricContractFile(BaseModel):
    """Container for governed KPI definitions."""

    metrics: list[MetricContract] = Field(min_length=1)


def load_metric_contracts(path: Path = CONTRACT_PATH) -> MetricContractFile:
    """Load and validate metric contracts."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Metric contract root must be a mapping")

    contracts = MetricContractFile.model_validate(payload)
    ids = [metric.id for metric in contracts.metrics]
    if len(ids) != len(set(ids)):
        raise ValueError("Metric IDs must be unique")
    return contracts


def main() -> None:
    contracts = load_metric_contracts()
    implemented = sum(metric.status == "implemented" for metric in contracts.metrics)
    deferred = sum(metric.status == "deferred" for metric in contracts.metrics)
    print(f"Validated {len(contracts.metrics)} KPI contracts.")
    print(f"Implemented: {implemented}; deferred: {deferred}.")


if __name__ == "__main__":
    main()
