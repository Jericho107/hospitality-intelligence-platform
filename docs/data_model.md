# Data Model

## Modelling objective

The warehouse must support analysis across property, outlet, product, supplier, channel and time without duplicating business logic in each dashboard page.

## Target dimensions

### dim_date
Calendar, fiscal attributes, weekday/weekend and hospitality operating periods.

### dim_property
Synthetic hotel/property entity.

### dim_outlet
Restaurant, bar, breakfast, room service or other F&B outlet.

### dim_product
Sellable or inventory product with food/beverage classification.

### dim_supplier
Synthetic purchasing supplier.

### dim_employee_role
Role-level labour dimension. No employee identity is required for the public case.

### dim_channel
Direct, OTA and other room-distribution channels.

## Target facts

### fact_room_nights
Grain: property × stay date × channel.

Measures:
- available room nights;
- occupied room nights;
- room revenue;
- distribution cost.

### fact_fnb_sales
Grain: POS transaction line.

Measures:
- quantity;
- net revenue;
- discount;
- theoretical product usage where recipe mapping applies.

### fact_purchases
Grain: purchase order line.

Measures:
- purchased quantity;
- actual unit cost;
- standard unit cost;
- extended purchase value.

### fact_inventory_movements
Grain: stock movement.

Measures:
- quantity;
- unit cost;
- movement value.

### fact_labour
Grain: role-level shift.

Measures:
- paid hours;
- labour cost.

### fact_budget
Grain: property/outlet/date/account.

Measures:
- budget amount.

## Modelling risks to reverse-test

- double counting revenue after joining line-level facts;
- many-to-many product mappings;
- slowly changing standard cost;
- outlet transfers counted as consumption;
- room inventory duplicated by channel;
- budget and actual grain mismatch.

These risks must be tested before the dimensional model can be considered validated.
