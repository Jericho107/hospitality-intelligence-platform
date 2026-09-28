from pathlib import Path

import pandas as pd

from hospitality_intelligence.forecasting import (
    build_features,
    load_contract,
    temporal_split,
)


def _series(days: int = 240) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=days, freq="D")
    rows = []
    for property_id, rooms in [("P001", 100), ("P002", 200)]:
        for index, current in enumerate(dates):
            rows.append(
                {
                    "date": current,
                    "property_id": property_id,
                    "rooms_available": rooms,
                    "rooms_sold": 50 + (index % 7) + (10 if property_id == "P002" else 0),
                }
            )
    return pd.DataFrame(rows)


def test_target_derived_features_respect_forecast_horizon() -> None:
    contract = load_contract()
    horizon = int(contract["protocol"]["horizon_days"])
    lags = [int(value) for value in contract["protocol"]["target_lags"]]

    assert min(lags) >= horizon


def test_future_target_mutation_cannot_change_prior_features() -> None:
    contract = load_contract()
    source = _series()
    cutoff = pd.Timestamp("2026-06-01")

    original = build_features(source, contract)
    mutated = source.copy()
    mutated.loc[mutated["date"] > cutoff, "rooms_sold"] = 9999
    rebuilt = build_features(mutated, contract)

    feature_columns = [
        column
        for column in original.columns
        if column not in {"rooms_sold"}
    ]
    left = original[original["date"] <= cutoff][feature_columns].reset_index(drop=True)
    right = rebuilt[rebuilt["date"] <= cutoff][feature_columns].reset_index(drop=True)

    pd.testing.assert_frame_equal(left, right)


def test_temporal_split_is_strictly_ordered() -> None:
    contract = load_contract()
    frame = build_features(_series(days=420), contract)
    train, validation, test = temporal_split(frame, contract)

    assert train["date"].max() < validation["date"].min()
    assert validation["date"].max() < test["date"].min()
