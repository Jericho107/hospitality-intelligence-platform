"""Validate the executive BI contract against governed KPI contracts."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

from hospitality_intelligence.metric_contracts import load_metric_contracts

ROOT = Path(__file__).resolve().parents[2]
BI_CONTRACT = ROOT / "config" / "bi_contract.yml"
DAX_PATH = ROOT / "powerbi" / "dax" / "measures.dax"
DAX_MEASURE_RE = re.compile(r"^\[([^\]]+)\]\s*=", re.MULTILINE)


class BIMeasure(BaseModel):
    name: str = Field(min_length=1)
    metric_id: str = Field(min_length=1)
    display_folder: str = Field(min_length=1)
    format: str = Field(min_length=1)
    executive: bool


class BIVisual(BaseModel):
    type: str = Field(min_length=1)
    purpose: str = Field(min_length=10)


class BIPage(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    decision_question: str = Field(min_length=15)
    measures: list[str] = Field(min_length=1)
    visuals: list[BIVisual] = Field(min_length=1)


class BIContract(BaseModel):
    measures: list[BIMeasure] = Field(min_length=1)
    deferred_metrics: list[str] = Field(default_factory=list)
    pages: list[BIPage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_uniqueness(self) -> BIContract:
        names = [measure.name for measure in self.measures]
        metric_ids = [measure.metric_id for measure in self.measures]
        page_ids = [page.id for page in self.pages]
        if len(names) != len(set(names)):
            raise ValueError("BI measure names must be unique")
        if len(metric_ids) != len(set(metric_ids)):
            raise ValueError("Each governed metric may map to one canonical BI measure")
        if len(page_ids) != len(set(page_ids)):
            raise ValueError("BI page IDs must be unique")
        return self


def load_bi_contract(path: Path = BI_CONTRACT) -> BIContract:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("BI contract root must be a mapping")
    return BIContract.model_validate(payload)


def dax_measure_names(path: Path = DAX_PATH) -> set[str]:
    return set(DAX_MEASURE_RE.findall(path.read_text(encoding="utf-8")))


def validate_bi_contract(
    bi_path: Path = BI_CONTRACT,
    dax_path: Path = DAX_PATH,
    metric_path: Path | None = None,
) -> BIContract:
    bi = load_bi_contract(bi_path)
    metrics = load_metric_contracts(metric_path) if metric_path else load_metric_contracts()

    metric_by_id = {metric.id: metric for metric in metrics.metrics}
    bi_names = {measure.name for measure in bi.measures}
    bi_metric_ids = {measure.metric_id for measure in bi.measures}
    dax_names = dax_measure_names(dax_path)

    unknown_metric_ids = bi_metric_ids - set(metric_by_id)
    if unknown_metric_ids:
        raise ValueError(f"Unknown metric IDs in BI contract: {sorted(unknown_metric_ids)}")

    deferred_used = {
        measure.metric_id
        for measure in bi.measures
        if metric_by_id[measure.metric_id].status != "implemented"
    }
    if deferred_used:
        raise ValueError(f"Deferred metrics exposed in BI: {sorted(deferred_used)}")

    if dax_names != bi_names:
        missing_in_dax = sorted(bi_names - dax_names)
        undocumented_dax = sorted(dax_names - bi_names)
        raise ValueError(
            "DAX/BI contract mismatch: "
            f"missing_in_dax={missing_in_dax}, undocumented_dax={undocumented_dax}"
        )

    deferred_contract_ids = {
        metric.id for metric in metrics.metrics if metric.status == "deferred"
    }
    if set(bi.deferred_metrics) != deferred_contract_ids:
        raise ValueError("BI deferred metrics must exactly match metric contracts")

    for page in bi.pages:
        unknown_names = set(page.measures) - bi_names
        if unknown_names:
            raise ValueError(
                f"{page.id}: unknown BI measures: {sorted(unknown_names)}"
            )

    executive_measures = {measure.name for measure in bi.measures if measure.executive}
    executive_page = next(
        (page for page in bi.pages if page.id == "executive_command_center"),
        None,
    )
    if executive_page is None:
        raise ValueError("Executive Command Center page is required")
    if not executive_measures.issubset(set(executive_page.measures)):
        missing = sorted(executive_measures - set(executive_page.measures))
        raise ValueError(f"Executive page missing measures: {missing}")

    return bi


def main() -> None:
    contract = validate_bi_contract()
    print(f"Validated {len(contract.measures)} governed BI measures.")
    print(f"Validated {len(contract.pages)} decision pages.")
    print("Deferred metrics remain blocked from BI exposure.")


if __name__ == "__main__":
    main()
