# Reverse-Test Plan

The flagship is validated by trying to make its own claims fail.

## Phase 1 — source-system trust

- mutate POS product-mix revenue while leaving outlet-check revenue unchanged;
- require cross-source validation to fail;
- regenerate the source state;
- require validation to recover to PASS.

Additional unit-level reverse tests cover broken purchase arithmetic and inventory roll-forward identities.

## Phase 2 — analytical store

Planned tests:

- mutate PostgreSQL target values without changing the source;
- require source-to-target reconciliation to fail;
- inject an orphan dimension key;
- require warehouse integrity controls to fail.

## Phase 3 — KPI layer

Planned tests:

- introduce conflicting KPI definitions;
- require the metric contract test to fail;
- alter cost-scope assumptions and verify contribution changes transparently.

## Phase 4 — analytical conclusions

Planned tests:

- compare `margin_leakage` with `healthy` scenario outputs;
- verify that the diagnostic ranking changes when the synthetic driver changes;
- prevent claims that are not stable across reasonable assumptions.

## Phase 5 — forecasting

Planned tests:

- compare every predictive approach against a naive baseline;
- reject the model if it does not materially improve the chosen error metric;
- test temporal rather than random holdout logic.
