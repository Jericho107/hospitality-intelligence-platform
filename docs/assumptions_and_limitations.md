# Assumptions and Limitations

## Synthetic data

All current sources are generated. They are designed to exercise analytical and engineering controls, not to represent a statistically valid hospitality benchmark.

## Controlled scenario

The `margin_leakage` scenario deliberately injects stronger beverage purchasing, waste and F&B labour pressure into the synthetic leisure resort near the end of the period. Demand also strengthens slightly.

The scenario exists so future diagnostics can be evaluated against a known construction. It must not be described as a discovered real-world insight.

## Source-system simplifications

- PMS demand is modelled at daily rather than booking-event grain.
- POS checks and product mix are represented as daily aggregates, not individual checks.
- Inventory products are simplified sellable/consumable units rather than full recipe/BOM structures.
- Procurement does not yet model lead time, purchase orders or invoice settlement.
- Labour does not yet model employee-level contracts, breaks or legal scheduling constraints.
- Shared overhead allocation is not yet governed.

## Raw landing design

All raw PostgreSQL columns are text by design. The raw layer preserves the source representation for exact source-to-target reconciliation.

Typed fields, relational keys and check constraints live in the analytical schema.

## Dimensional-history limitation

Analytical dimensions are rebuilt as Type-1 snapshots. Slowly changing dimension history is not modelled in the current case study.

## Budget date convention

Monthly budgets use the first calendar day of each month as their date key.

## Current implementation boundary

Phase 2 proves source generation, source contracts, PostgreSQL raw ingestion, exact source-to-raw reconciliation, dimensional modelling and raw-to-analytics controls.

KPI materialisation, Power BI, statistical diagnostics, forecasting and quantified business action remain future work and receive no current scoring credit.
