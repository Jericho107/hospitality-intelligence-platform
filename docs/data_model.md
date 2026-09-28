# Dimensional Data Model

## Grain discipline

Facts remain separate when their natural grains differ. The project deliberately avoids a single convenience table that would duplicate measures or obscure business meaning.

| Fact | Grain | Core measures |
|---|---|---|
| `fact_room_inventory_daily` | property × day | rooms available |
| `fact_room_bookings_daily` | property × day × segment × channel | rooms sold, room revenue |
| `fact_pos_outlet_daily` | property × outlet × day | covers, gross, discount, net revenue |
| `fact_pos_product_daily` | property × outlet × product × day | units sold, net revenue |
| `fact_purchases_daily` | property × product × supplier × day | quantity, unit cost, purchase cost |
| `fact_inventory_daily` | property × product × day | opening, receipts, usage, waste, closing, value |
| `fact_labour_daily` | property × department × day | scheduled, actual, overtime, labour cost |
| `fact_budget_monthly` | property × department × month | budget revenue, budget cost |

## Dimensions

- `dim_date`
- `dim_property`
- `dim_outlet`
- `dim_product`
- `dim_supplier`
- `dim_department`
- `dim_room_segment`
- `dim_channel`

Surrogate keys are used in the analytical schema while source business identifiers remain unique attributes.

## Why rooms are split

Room inventory exists at property-day grain while booked rooms exist at property-day-segment-channel grain.

Combining them into one fact would repeat room inventory across segment/channel combinations and make occupancy denominators unsafe unless every downstream consumer understood the duplication.

The model therefore keeps two facts and allows governed measures to aggregate each at its native grain.

## Current dimension policy

Dimensions are rebuilt as Type-1 snapshots for this synthetic case study.

Slowly changing dimension history is not currently modelled and must not be inferred from this phase.
