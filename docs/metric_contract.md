# Metric Contract

Metrics are not considered trusted because they appear on a dashboard. Each one requires a defined grain, numerator, denominator, source and limitation.

| Metric | Definition | Source grain | Current status |
|---|---|---|---|
| Occupancy | rooms sold / rooms available | property-day | defined, not yet materialised |
| ADR | room revenue / rooms sold | property-day | defined, not yet materialised |
| RevPAR | room revenue / rooms available | property-day | defined, not yet materialised |
| Net F&B Revenue | gross revenue - discounts | outlet-day | source identity validated |
| Average Check | net F&B revenue / covers | outlet-day | defined, not yet materialised |
| Discount Rate | discount amount / gross revenue | outlet-day | defined, not yet materialised |
| Purchase Price Variance | actual unit cost - standard unit cost, quantity weighted | product/property/day | defined, not yet materialised |
| Waste Cost | waste quantity × weighted unit cost | product/property/day | defined, not yet materialised |
| Labour Cost % | labour cost / relevant department revenue | department/property/period | defined, not yet materialised |
| Budget Variance | actual - budget | property/department/period | defined, not yet materialised |
| Controllable Contribution | governed revenue less explicitly scoped controllable costs | property/department/period | definition pending final cost-scope review |

## Important boundary

`Controllable Contribution` is intentionally not finalised in Phase 1. The repository will not publish a contribution result until the cost scope, treatment of shared operations and allocation policy are documented and tested.
