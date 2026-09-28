# Metric Contracts

The canonical machine-readable definitions live in:

```text
config/metric_contracts.yml
```

## Why contracts exist

Hospitality metrics often look simple while hiding material definition choices.

Examples:

- Does occupancy exclude out-of-order rooms?
- Does ADR include complimentary rooms?
- Does room revenue include tax?
- Is distribution cost included in RevPAR?
- Does F&B cost include labour?
- Are transfers neutralized in inventory consumption?
- Does labour cost include employer taxes?

A dashboard that does not answer these questions is not governed.

## Current governed metrics

- Occupancy %
- ADR
- RevPAR
- Net RevPAR
- F&B Gross Margin %
- Food Cost %
- Beverage Cost %
- Purchase Price Variance
- Inventory Variance Value
- Labour Cost %
- Revenue per Labour Hour
- Demand Forecast WAPE

Each contract contains purpose, formula, grain, sources, owner, refresh cadence, exclusions, reconciliation rule and limitations.

## Rule

The Power BI implementation will consume these definitions; it will not silently redefine them.
