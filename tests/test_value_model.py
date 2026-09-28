from pathlib import Path

from hospitality_intelligence.generate_synthetic_data import GenerationConfig, generate
from hospitality_intelligence.value_model import evaluate


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


def test_value_model_never_labels_estimate_as_realized_savings(tmp_path: Path) -> None:
    result = evaluate(_scenario(tmp_path, "margin_leakage"))
    combined = " ".join(
        [
            *(item.action for item in result.opportunities),
            *(item.limitation for item in result.opportunities),
        ]
    ).lower()

    assert "realized savings" not in combined
