from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from hospitality_intelligence.validate_bi_contract import (
    BIContract,
    load_bi_contract,
    validate_bi_contract,
)


def test_repository_bi_contract_is_valid() -> None:
    contract = validate_bi_contract()

    assert len(contract.measures) == 11
    assert len(contract.pages) == 4
    assert "controllable_contribution" in contract.deferred_metrics
    assert "labour_cost_pct" in contract.deferred_metrics


def test_duplicate_bi_measure_names_are_rejected() -> None:
    contract = load_bi_contract()
    payload = contract.model_dump()
    payload["measures"].append(payload["measures"][0])

    with pytest.raises(ValidationError):
        BIContract.model_validate(payload)


def test_executive_page_uses_only_governed_measure_names() -> None:
    contract = load_bi_contract()
    known = {measure.name for measure in contract.measures}
    executive = next(
        page for page in contract.pages if page.id == "executive_command_center"
    )

    assert set(executive.measures).issubset(known)


def test_deferred_metric_cannot_be_exposed_in_bi(tmp_path: Path) -> None:
    contract = load_bi_contract()
    payload = contract.model_dump()
    payload["measures"].append(
        {
            "name": "Controllable Contribution",
            "metric_id": "controllable_contribution",
            "display_folder": "Management",
            "format": "$#,0",
            "executive": False,
        }
    )
    bi_path = tmp_path / "bi_contract.yml"
    bi_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    dax_path = tmp_path / "measures.dax"
    dax_path.write_text(
        (Path(__file__).resolve().parents[1] / "powerbi" / "dax" / "measures.dax")
        .read_text(encoding="utf-8")
        + "\n[Controllable Contribution] = 0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Deferred metrics exposed in BI"):
        validate_bi_contract(bi_path=bi_path, dax_path=dax_path)
