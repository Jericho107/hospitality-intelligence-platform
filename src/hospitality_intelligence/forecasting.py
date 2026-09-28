"""Baseline-first seven-day-ahead room-demand forecasting."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "config" / "forecast_contract.yml"

CandidateName = Literal["hist_gradient_boosting", "zero"]


@dataclass(frozen=True)
class Metrics:
    wape: float
    mae: float


@dataclass(frozen=True)
class Evaluation:
    candidate: str
    selected_on_validation: bool
    accepted_on_test: bool
    baseline_validation: Metrics
    candidate_validation: Metrics
    baseline_test: Metrics
    candidate_test: Metrics
    validation_wape_improvement: float
    test_wape_improvement: float
    worst_property_wape_regression: float
    property_test: dict[str, dict[str, float]]


def load_contract() -> dict[str, object]:
    payload = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Forecast contract root must be a mapping")
    return payload


def load_daily_demand(data_dir: Path) -> pd.DataFrame:
    """Aggregate validated PMS booking lines to property-day room demand."""

    bookings = pd.read_csv(data_dir / "pms_bookings_daily.csv")
    inventory = pd.read_csv(data_dir / "pms_inventory_daily.csv")

    bookings["date"] = pd.to_datetime(bookings["date"])
    inventory["date"] = pd.to_datetime(inventory["date"])

    demand = (
        bookings.groupby(["date", "property_id"], as_index=False)["rooms_sold"]
        .sum()
        .sort_values(["property_id", "date"])
    )
    data = demand.merge(
        inventory[["date", "property_id", "rooms_available"]],
        on=["date", "property_id"],
        how="inner",
        validate="one_to_one",
    )
    if data.empty:
        raise ValueError("No daily demand rows available")
    if (data["rooms_sold"] > data["rooms_available"]).any():
        raise ValueError("Forecast source contains rooms_sold > rooms_available")
    return data.sort_values(["property_id", "date"]).reset_index(drop=True)


def build_features(data: pd.DataFrame, contract: dict[str, object]) -> pd.DataFrame:
    """Build horizon-safe target features for a rolling seven-day-ahead forecast."""

    protocol = contract["protocol"]
    if not isinstance(protocol, dict):
        raise ValueError("protocol must be a mapping")

    horizon = int(protocol["horizon_days"])
    lags = [int(value) for value in protocol["target_lags"]]
    if min(lags) < horizon:
        raise ValueError("Every target-derived lag must be >= forecast horizon")

    rolling_window = int(protocol["rolling_window_days"])
    frame = data.copy().sort_values(["property_id", "date"])
    grouped = frame.groupby("property_id", group_keys=False)["rooms_sold"]

    for lag in lags:
        frame[f"lag_{lag}"] = grouped.shift(lag)

    shifted = grouped.shift(horizon)
    by_property = shifted.groupby(frame["property_id"], group_keys=False)
    frame[f"rolling_mean_{rolling_window}_at_horizon"] = by_property.transform(
        lambda series: series.rolling(rolling_window, min_periods=rolling_window).mean()
    )
    frame[f"rolling_std_{rolling_window}_at_horizon"] = by_property.transform(
        lambda series: series.rolling(rolling_window, min_periods=rolling_window).std()
    )

    frame["day_of_week"] = frame["date"].dt.dayofweek
    frame["dow_sin"] = frame["day_of_week"].map(
        lambda value: math.sin(2 * math.pi * value / 7)
    )
    frame["dow_cos"] = frame["day_of_week"].map(
        lambda value: math.cos(2 * math.pi * value / 7)
    )
    frame["day_of_year"] = frame["date"].dt.dayofyear
    frame["doy_sin"] = frame["day_of_year"].map(
        lambda value: math.sin(2 * math.pi * value / 365.25)
    )
    frame["doy_cos"] = frame["day_of_year"].map(
        lambda value: math.cos(2 * math.pi * value / 365.25)
    )

    required = [f"lag_{lag}" for lag in lags]
    required += [
        f"rolling_mean_{rolling_window}_at_horizon",
        f"rolling_std_{rolling_window}_at_horizon",
    ]
    return frame.dropna(subset=required).reset_index(drop=True)


def temporal_split(
    frame: pd.DataFrame,
    contract: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create chronological train/validation/test partitions."""

    protocol = contract["protocol"]
    if not isinstance(protocol, dict):
        raise ValueError("protocol must be a mapping")

    validation_days = int(protocol["validation_days"])
    test_days = int(protocol["test_days"])
    minimum_training_days = int(protocol["minimum_training_days"])

    max_date = frame["date"].max()
    test_start = max_date - pd.Timedelta(days=test_days - 1)
    validation_start = test_start - pd.Timedelta(days=validation_days)

    train = frame[frame["date"] < validation_start].copy()
    validation = frame[
        (frame["date"] >= validation_start) & (frame["date"] < test_start)
    ].copy()
    test = frame[frame["date"] >= test_start].copy()

    training_span = (train["date"].max() - train["date"].min()).days + 1
    if training_span < minimum_training_days:
        raise ValueError(
            f"Training window too short: {training_span} < {minimum_training_days}"
        )
    if validation.empty or test.empty:
        raise ValueError("Validation and test windows must both contain data")
    if not (
        train["date"].max() < validation["date"].min()
        and validation["date"].max() < test["date"].min()
    ):
        raise ValueError("Temporal partitions overlap")

    return train, validation, test


def feature_columns(contract: dict[str, object]) -> tuple[list[str], list[str]]:
    protocol = contract["protocol"]
    if not isinstance(protocol, dict):
        raise ValueError("protocol must be a mapping")

    lags = [int(value) for value in protocol["target_lags"]]
    rolling_window = int(protocol["rolling_window_days"])
    numeric = [
        "rooms_available",
        *[f"lag_{lag}" for lag in lags],
        f"rolling_mean_{rolling_window}_at_horizon",
        f"rolling_std_{rolling_window}_at_horizon",
        "dow_sin",
        "dow_cos",
        "doy_sin",
        "doy_cos",
    ]
    return numeric, ["property_id"]


def build_model(contract: dict[str, object]) -> Pipeline:
    candidate = contract["candidate"]
    protocol = contract["protocol"]
    if not isinstance(candidate, dict) or not isinstance(protocol, dict):
        raise ValueError("candidate and protocol must be mappings")

    numeric, categorical = feature_columns(contract)
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", numeric),
            (
                "property",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical,
            ),
        ],
        remainder="drop",
    )
    model = HistGradientBoostingRegressor(
        max_iter=int(candidate["max_iter"]),
        learning_rate=float(candidate["learning_rate"]),
        max_leaf_nodes=int(candidate["max_leaf_nodes"]),
        l2_regularization=float(candidate["l2_regularization"]),
        random_state=int(protocol["random_state"]),
    )
    return Pipeline([("features", preprocessing), ("model", model)])


def _metrics(actual: pd.Series, predicted: pd.Series) -> Metrics:
    errors = (actual - predicted).abs()
    denominator = float(actual.abs().sum())
    if denominator == 0:
        raise ValueError("WAPE denominator is zero")
    return Metrics(
        wape=float(errors.sum() / denominator),
        mae=float(errors.mean()),
    )


def _improvement(baseline: float, candidate: float) -> float:
    if baseline <= 0:
        raise ValueError("Baseline metric must be positive")
    return (baseline - candidate) / baseline


def _predict(
    candidate: CandidateName,
    model: Pipeline | None,
    frame: pd.DataFrame,
) -> pd.Series:
    if candidate == "zero":
        return pd.Series(0.0, index=frame.index)
    if model is None:
        raise ValueError("Model is required for ML candidate")
    values = model.predict(frame)
    return pd.Series(values, index=frame.index).clip(lower=0)


def evaluate(
    data_dir: Path,
    candidate: CandidateName = "hist_gradient_boosting",
) -> Evaluation:
    """Select on validation, refit if selected, then evaluate untouched test."""

    contract = load_contract()
    data = load_daily_demand(data_dir)
    frame = build_features(data, contract)
    train, validation, test = temporal_split(frame, contract)

    baseline_validation_pred = validation["lag_7"]
    baseline_test_pred = test["lag_7"]
    baseline_validation = _metrics(validation["rooms_sold"], baseline_validation_pred)
    baseline_test = _metrics(test["rooms_sold"], baseline_test_pred)

    if candidate == "zero":
        validation_pred = _predict(candidate, None, validation)
        test_pred = _predict(candidate, None, test)
    else:
        model = build_model(contract)
        model.fit(train, train["rooms_sold"])
        validation_pred = _predict(candidate, model, validation)

        accepted_for_refit = _improvement(
            baseline_validation.wape,
            _metrics(validation["rooms_sold"], validation_pred).wape,
        ) >= float(contract["acceptance"]["minimum_validation_wape_improvement"])

        if accepted_for_refit:
            refit = build_model(contract)
            train_validation = pd.concat([train, validation], ignore_index=True)
            refit.fit(train_validation, train_validation["rooms_sold"])
            test_pred = _predict(candidate, refit, test)
        else:
            test_pred = _predict("zero", None, test)

    candidate_validation = _metrics(validation["rooms_sold"], validation_pred)
    candidate_test = _metrics(test["rooms_sold"], test_pred)
    validation_improvement = _improvement(
        baseline_validation.wape, candidate_validation.wape
    )
    test_improvement = _improvement(baseline_test.wape, candidate_test.wape)

    acceptance = contract["acceptance"]
    selected = validation_improvement >= float(
        acceptance["minimum_validation_wape_improvement"]
    )

    property_test: dict[str, dict[str, float]] = {}
    worst_regression = 0.0
    for property_id, rows in test.assign(
        baseline_prediction=baseline_test_pred,
        candidate_prediction=test_pred,
    ).groupby("property_id"):
        base = _metrics(rows["rooms_sold"], rows["baseline_prediction"])
        cand = _metrics(rows["rooms_sold"], rows["candidate_prediction"])
        regression = max(0.0, (cand.wape - base.wape) / base.wape)
        worst_regression = max(worst_regression, regression)
        property_test[str(property_id)] = {
            "baseline_wape": base.wape,
            "candidate_wape": cand.wape,
            "wape_improvement": _improvement(base.wape, cand.wape),
        }

    accepted_test = (
        selected
        and test_improvement
        >= float(acceptance["minimum_test_wape_improvement"])
        and worst_regression
        <= float(acceptance["maximum_property_wape_regression"])
        and candidate_test.mae < baseline_test.mae
    )

    return Evaluation(
        candidate=candidate,
        selected_on_validation=selected,
        accepted_on_test=accepted_test,
        baseline_validation=baseline_validation,
        candidate_validation=candidate_validation,
        baseline_test=baseline_test,
        candidate_test=candidate_test,
        validation_wape_improvement=validation_improvement,
        test_wape_improvement=test_improvement,
        worst_property_wape_regression=worst_regression,
        property_test=property_test,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate governed room-demand forecast.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument(
        "--candidate",
        choices=["hist_gradient_boosting", "zero"],
        default="hist_gradient_boosting",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expect", choices=["accepted", "rejected"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate(args.data_dir, args.candidate)
    payload = asdict(result)
    print(json.dumps(payload, indent=2))

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.expect == "accepted" and not result.accepted_on_test:
        raise SystemExit("Forecast candidate was not accepted.")
    if args.expect == "rejected" and (
        result.selected_on_validation or result.accepted_on_test
    ):
        raise SystemExit("Forecast candidate was expected to be rejected.")


if __name__ == "__main__":
    main()
