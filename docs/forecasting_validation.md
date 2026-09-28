# Forecasting Validation

## Decision question

Can the system improve a seven-day-ahead room-demand forecast enough to justify using a predictive model instead of a simple seasonal rule?

## Protocol

The experiment is intentionally baseline-first.

- target: rooms sold;
- grain: property × day;
- horizon: 7 days;
- source: validated PMS booking data;
- dedicated synthetic horizon: 420 days;
- validation window: 56 days;
- final test window: 84 days;
- baseline: seasonal naive, target date = observed demand 7 days earlier;
- candidate: HistGradientBoostingRegressor;
- metrics: WAPE and MAE.

Model selection occurs on the validation period. The final test period is evaluated only after the candidate passes the validation gate.

## Leakage controls

Every target-derived feature uses information at least seven days old.

Target lags:

- 7;
- 14;
- 21;
- 28;
- 35;
- 42;
- 56 days.

Rolling statistics are shifted by the seven-day forecast horizon before calculation.

The test suite also mutates future target values and proves that already-available historical feature rows do not change.

## Acceptance contract

A candidate must:

1. improve validation WAPE by at least 2% versus seasonal naive;
2. not worsen final-test WAPE versus baseline;
3. improve final-test MAE;
4. avoid more than 10% WAPE regression on any property.

A deliberately useless zero-demand predictor must be rejected.

## Interpretation boundary

This is a rolling seven-day-ahead evaluation, not one static 84-day forecast.

Synthetic performance does not establish production forecast performance. The current synthetic source omits booking pace, cancellations, events, pricing changes, weather, competitor rates and other material exogenous signals.

If the candidate does not beat the baseline under the fixed protocol, the correct outcome is to keep the baseline.
