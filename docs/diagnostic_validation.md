# Diagnostic Validation

## Objective

Phase 4 tests whether the analytical logic can recover the drivers deliberately injected into the synthetic hospitality scenario.

This is not causal proof and it is not a production counterfactual capability.

## Benchmark design

Two source systems are generated with identical seed, identical date horizon, identical property structure and identical random sequence. Only the scenario flag changes.

The healthy and margin-leakage datasets are compared by a paired diagnostic benchmark.

## Expected injected drivers

For the controlled leisure resort (P002), the leakage scenario injects:

- beverage unit-cost pressure;
- beverage waste pressure;
- F&B labour/overtime pressure;
- modest additional room and F&B demand.

The diagnostic engine must detect the three adverse cost drivers.

## Negative control

The same engine is also run as healthy versus healthy.

Expected result: no adverse driver.

This prevents a detector that simply reports leakage regardless of evidence from receiving credit.

## Interpretation boundary

The benchmark demonstrates that analytical logic can recover known synthetic signals.

It does not prove:

- causality in real hotel operations;
- generalization to arbitrary PMS/POS systems;
- production alert thresholds;
- realized financial impact.

Those require separate evidence.
