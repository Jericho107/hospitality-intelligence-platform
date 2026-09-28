# Metric Contract

## Governance rule

A metric is not trusted because its formula is familiar or because it appears in a dashboard.

The canonical machine-readable contract is:

```text
config/metric_contracts.yml
```

Every metric must define business purpose, grain, formula, governed sources, owner, exclusions, reconciliation rule, limitations and implementation status.

## Implemented in Phase 3

| Metric | Grain | Materialized mart |
|---|---|---|
| Occupancy % | property × day | `kpi_rooms_daily` |
| ADR | property × day | `kpi_rooms_daily` |
| RevPAR | property × day | `kpi_rooms_daily` |
| Net F&B Revenue | property × outlet × day | `kpi_fnb_outlet_daily` |
| Average Check | property × outlet × day | `kpi_fnb_outlet_daily` |
| Discount Rate | property × outlet × day | `kpi_fnb_outlet_daily` |
| Purchase Price Variance | property × product × supplier × day | `kpi_purchasing_daily` |
| Waste Cost | property × product × day | `kpi_inventory_daily` |
| Waste % | property × product × day | `kpi_inventory_daily` |
| Labour Cost per Hour | property × department × day | `kpi_labour_daily` |
| Overtime Share | property × department × day | `kpi_labour_daily` |

## Deliberately deferred

### Labour Cost %

The numerator exists. The denominator does not yet have a sufficiently governed department-revenue allocation policy across Rooms, F&B and Operations.

Publishing this percentage now would create false precision.

### Controllable Contribution

Shared-cost scope and allocation remain unresolved.

The flagship's management question references controllable contribution as the target decision problem, but the repository does **not** publish the metric until the cost contract is explicit and reverse-tested.

## Reverse test

Phase 3 materializes KPI tables and validates them independently from the build SQL.

CI then changes one materialized ADR while leaving the underlying facts unchanged.

Expected behavior:

```text
clean facts
→ build KPI marts
→ metric validation PASS
→ mutate ADR only
→ metric validation FAIL
→ rebuild KPI marts
→ metric validation PASS
```

This proves that the metric layer is controlled independently from the warehouse layer.
