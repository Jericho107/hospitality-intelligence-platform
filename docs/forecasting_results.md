# Forecasting Results — Synthetic Benchmark

## Evidence run

GitHub Actions run #26 evaluated the fixed forecasting protocol after all prior Phase 1–5 gates passed.

These results are synthetic benchmark evidence only. They are not production hotel forecast performance.

## Seed 42 — primary evaluation

| Metric | Seasonal naive | HistGradientBoosting | Relative change |
|---|---:|---:|---:|
| Validation WAPE | 5.64% | 4.27% | 24.35% improvement |
| Validation MAE | 5.58 | 4.22 | lower |
| Final-test WAPE | 6.00% | 3.76% | 37.29% improvement |
| Final-test MAE | 5.85 | 3.67 | lower |

Worst property WAPE regression: 0%.

Property-level test WAPE improved for all three synthetic properties.

## Robustness seeds

### Seed 7

- validation WAPE improvement: 17.27%;
- final-test WAPE improvement: 36.91%;
- worst property WAPE regression: 0%.

### Seed 107

- validation WAPE improvement: 30.91%;
- final-test WAPE improvement: 40.08%;
- worst property WAPE regression: 0%.

## Negative control

A zero-demand predictor was evaluated by the same selection contract.

Validation WAPE:

- seasonal naive: 5.64%;
- zero predictor: 100%.

The zero predictor was rejected before the final-test period was unlocked.

## Interpretation

The evidence supports a narrow conclusion:

> Under this fixed synthetic room-demand protocol, the HistGradientBoosting candidate adds measurable predictive value over a seven-day seasonal-naive baseline.

It does not support claims about production hotel accuracy.

Material missing production signals include booking pace, cancellations, events, pricing, weather, competitor rates and external demand indicators.
