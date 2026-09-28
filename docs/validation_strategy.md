# Validation Strategy

## Principle

The repository must prove both the success path and the failure path.

## Gate 0 — Governance

Current foundation gate:

- source contracts parse;
- metric contracts parse;
- IDs are unique;
- source references are valid;
- source primary keys are required fields;
- financial fields exist in source schemas;
- every metric has exclusions, reconciliation and limitations;
- Ruff passes;
- pytest passes.

## Gate 1 — Synthetic sources

Future acceptance:

- row counts match generation parameters;
- primary keys are unique;
- declared PII boundary is respected;
- injected source defects are detectable;
- generation is reproducible for a fixed seed and anchor.

## Gate 2 — Warehouse

Future acceptance:

- referential integrity;
- fact grain uniqueness;
- source-to-target row reconciliation;
- financial control-total reconciliation;
- dimensional unknown-member handling;
- no silent row multiplication.

## Gate 3 — Metrics

Future acceptance:

- SQL implementation matches metric contract;
- algebraic identities hold where applicable;
- warehouse KPI totals reconcile to independent control calculations;
- corrupted numerator/denominator causes test failure.

## Gate 4 — Power BI

Future acceptance:

- headline KPIs reconcile to warehouse extracts;
- filters do not change grain unexpectedly;
- DAX definitions are documented;
- no hidden KPI logic conflicts with canonical contracts.

## Gate 5 — Forecasting

Future acceptance:

- time-aware split;
- naive baseline;
- error metric selected before model comparison;
- leakage checks;
- residual/bias diagnostics;
- model rejected if it does not materially beat baseline.

## Gate 6 — Business recommendation

Future acceptance:

Every recommendation must state:

- observed signal;
- causal limitation;
- proposed action;
- expected mechanism;
- measurement metric;
- review window;
- downside/risk.

## Gate 7 — Officialisation

Final requirements:

- all critical CI gates green;
- documentation links valid;
- no unsupported claims;
- reverse tests demonstrated;
- severe-review score >= 92;
- no critical blocker.

A score >= 92 does not override a critical blocker.
