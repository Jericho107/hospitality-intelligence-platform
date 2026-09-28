# Assumptions and Limitations

## Synthetic data

All current sources are generated. They are designed to exercise analytical and engineering controls, not to represent a statistically valid hospitality benchmark.

## Controlled scenario

The `margin_leakage` scenario deliberately injects stronger beverage purchasing, waste and F&B labour pressure into the synthetic leisure resort near the end of the period. This exists so the future diagnostic layer can be tested against a known causal construction.

It must not be described as a discovered real-world insight.

## Source-system simplifications

- PMS demand is modelled at daily rather than booking-event grain.
- POS checks and product mix are represented as daily aggregates, not individual checks.
- Inventory products are simplified sellable/consumable units rather than full recipe/BOM structures.
- Procurement does not yet model lead time, purchase orders or invoice settlement.
- Labour does not yet model employee-level contracts, breaks or legal scheduling constraints.
- Shared overhead allocation is not defined in Phase 1.

## Current implementation boundary

Phase 1 proves source generation, contracts and cross-source validation. PostgreSQL modelling, KPI marts, Power BI, statistical diagnostics and forecasting remain future work and receive no current scoring credit.
