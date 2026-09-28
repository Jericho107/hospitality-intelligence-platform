from pathlib import Path

import pytest
import yaml

from hospitality_intelligence.generate_synthetic_data import GenerationConfig, generate
from hospitality_intelligence.value_model import CONTRACT_PATH, evaluate, load_contract


def _scenario(tmp_path: Path, scenario: str) -> Path:
    target = tmp_path / scenario
    generate(
        GenerationConfig(days=60, seed=42, scenario=scenario),
        target,
    )
    return target


def test_value_model_is_bounded_and_non_negative(tmp_path: Path) -> None:
    result = evaluate(_scenario(tmp_path, "margin_leakage"))

    assert result.conservative_total >= 0
    assert result.base_total >= result.conservative_total
    assert result.stretch_total >= result.base_total
    assert all(item.observed_exposure >= 0 for item in result.opportunities)


def test_leakage_scenario_creates_more_modeled_opportunity_than_healthy(
    tmp_path: Path,
) -> None:
    healthy = evaluate(_scenario(tmp_path, "healthy"))
    leakage = evaluate(_scenario(tmp_path, "margin_leakage"))

    assert leakage.base_total > healthy.base_total * 2
    healthy_map = {item.driver: item.observed_exposure for item in healthy.opportunities}
    leakage_map = {item.driver: item.observed_exposure for item in leakage.opportunities}

    for driver in {"purchase_price", "waste", "overtime_premium"}:
        assert leakage_map[driver] > healthy_map[driver]


def test_action_labels_do_not_claim_realized_savings(tmp_path: Path) -> None:
    result = evaluate(_scenario(tmp_path, "margin_leakage"))

    assert all("realized" not in item.action.lower() for item in result.opportunities)


def test_recovery_assumptions_must_be_bounded_and_ordered(tmp_path: Path) -> None:
    payload = load_contract()
    payload["recovery_scenarios"]["base"] = 1.20
    path = tmp_path / "invalid_value_contract.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="Recovery scenarios"):
        load_contract(path)


def test_repository_contract_path_exists() -> None:
    assert CONTRACT_PATH.exists()
