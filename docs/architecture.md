# Architecture

## Architectural principle

The platform is a management decision system, not a collection of dashboards.

Each layer has one responsibility:

```text
Operational source
→ contract
→ validation
→ transformation
→ warehouse
→ governed metric
→ analysis
→ decision surface
→ action
→ outcome measurement
```

## Target layers

### 1. Synthetic operational sources

Six source-system families are planned:

- PMS;
- POS;
- purchasing;
- inventory;
- workforce/labour;
- finance budget.

Their schemas are governed by `config/source_contracts.yml`.

### 2. Validation

Before a record can enter the analytical layer, controls will evaluate:

- schema;
- key uniqueness;
- required fields;
- domain validity;
- referential integrity;
- financial ranges;
- dates;
- freshness;
- cross-source consistency.

### 3. Transformation

Python will own orchestration and reusable validation/transformation components.

SQL will own set-based warehouse transformations and analytical modelling where SQL is the clearer execution surface.

### 4. PostgreSQL warehouse

The target is a dimensional analytical model.

Facts and dimensions are documented in [data_model.md](data_model.md).

### 5. Metric layer

Management KPIs are governed independently from visualizations.

The metric contract is the interface between business meaning and technical implementation.

### 6. Analytical models

Forecasting or statistical analysis will only be added when a baseline comparison demonstrates incremental value.

### 7. Power BI

Power BI is the decision surface.

It must not contain undisclosed business logic that diverges from the warehouse/metric contracts.

## Non-negotiable reverse tests

The architecture must eventually demonstrate:

1. source record loss is detected;
2. duplicate business keys are detected;
3. orphan dimensions are detected;
4. metric corruption is detected;
5. warehouse totals reconcile to source control totals;
6. Power BI headline metrics reconcile to warehouse outputs;
7. forecasting is rejected if it fails to beat a naive baseline.

## Production boundary

The portfolio case may demonstrate production-oriented controls, but it will not claim production readiness unless deployment, secrets, observability, recovery, capacity and operational ownership are actually implemented.
