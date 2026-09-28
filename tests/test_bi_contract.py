import pytest
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
