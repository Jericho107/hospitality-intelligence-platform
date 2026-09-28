from datetime import date
from pathlib import Path

import pytest

from hospitality_intelligence.contracts import (
    load_and_validate_sources,
)
from hospitality_intelligence.failure_injection import (
    inject_pos_revenue_mismatch,
)
from hospitality_intelligence.generate_synthetic_data import (
    GenerationConfig,
    generate,
)


def test_pos_revenue_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    generate(
        GenerationConfig(
            days=30,
            seed=7,
            anchor_date=date(2026, 9, 1),
        ),
        tmp_path,
    )
    load_and_validate_sources(tmp_path)

    inject_pos_revenue_mismatch(tmp_path)

    with pytest.raises(
        ValueError,
        match="POS cross-check failed",
    ):
        load_and_validate_sources(tmp_path)
