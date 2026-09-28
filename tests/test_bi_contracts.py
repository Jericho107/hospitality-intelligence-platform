from pathlib import Path

import pytest
import yaml

from hospitality_intelligence.bi_contracts import (
    RATIO_MEASURES,
    extract_tmdl_measures,
    validate_bi_assets,
)


def test_bi_assets_validate_cleanly() -> None:
    measure_count, visual_count = validate_bi_assets()

    assert measure_count >= 25
    assert visual_count >= 15


def test_ratio_measures_use_divide() -> None:
    tables = extract_tmdl_measures()
    measures = {name: expr for table in tables.values() for name, expr in table.items()}

    for name in RATIO_MEASURES:
        assert "DIVIDE(" in measures[name].upper()


def test_forbidden_measure_reference_fails_closed(tmp_path: Path) -> None:
    source = Path("config/report_contract.yml")
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["pages"][0]["visuals"][0]["measures"] = ["Controllable Contribution"]
    broken = tmp_path / "broken_report_contract.yml"
    broken.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="forbidden measure"):
        validate_bi_assets(broken)
