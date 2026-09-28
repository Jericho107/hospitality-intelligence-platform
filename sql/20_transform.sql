TRUNCATE TABLE
    analytics.fact_budget_monthly,
    analytics.fact_labour_daily,
    analytics.fact_inventory_daily,
    analytics.fact_purchases_daily,
    analytics.fact_pos_product_daily,
    analytics.fact_pos_outlet_daily,
    analytics.fact_room_bookings_daily,
    analytics.fact_room_inventory_daily,
    analytics.dim_channel,
    analytics.dim_room_segment,
    analytics.dim_product,
    analytics.dim_supplier,
    analytics.dim_department,
    analytics.dim_outlet,
    analytics.dim_property,
    analytics.dim_date
RESTART IDENTITY CASCADE;

INSERT INTO analytics.dim_date (
    date_key,
    full_date,
    year_number,
    month_number,
    day_number,
    month_start,
    day_name,
    is_weekend
)
SELECT DISTINCT
    TO_CHAR(source_date, 'YYYYMMDD')::INTEGER,
    source_date,
    EXTRACT(YEAR FROM source_date)::INTEGER,
    EXTRACT(MONTH FROM source_date)::INTEGER,
    EXTRACT(DAY FROM source_date)::INTEGER,
    DATE_TRUNC('month', source_date)::DATE,
    TRIM(TO_CHAR(source_date, 'Day')),
    EXTRACT(ISODOW FROM source_date) IN (6, 7)
FROM (
    SELECT date::DATE AS source_date FROM raw.pms_inventory_daily
    UNION
    SELECT date::DATE FROM raw.pms_bookings_daily
    UNION
    SELECT date::DATE FROM raw.pos_checks_daily
    UNION
    SELECT date::DATE FROM raw.pos_product_mix_daily
    UNION
    SELECT date::DATE FROM raw.purchases_daily
    UNION
    SELECT date::DATE FROM raw.inventory_daily
    UNION
    SELECT date::DATE FROM raw.labour_daily
    UNION
    SELECT month::DATE FROM raw.budget_monthly
) dates;

INSERT INTO analytics.dim_property (
    property_id,
    property_name,
    archetype,
    rooms_count,
    city
)
SELECT
    property_id,
    property_name,
    archetype,
    rooms_count::INTEGER,
    city
FROM raw.properties
ORDER BY property_id;

INSERT INTO analytics.dim_outlet (
    outlet_id,
    property_key,
    outlet_name,
    outlet_type
)
SELECT
    o.outlet_id,
    p.property_key,
    o.outlet_name,
    o.outlet_type
FROM raw.outlets o
JOIN analytics.dim_property p USING (property_id)
ORDER BY o.outlet_id;

INSERT INTO analytics.dim_product (
    product_id,
    outlet_key,
    property_key,
    product_name,
    category,
    menu_price,
    standard_unit_cost,
    inventory_usage_per_unit
)
SELECT
    pr.product_id,
    o.outlet_key,
    p.property_key,
    pr.product_name,
    pr.category,
    pr.menu_price::NUMERIC(14,2),
    pr.standard_unit_cost::NUMERIC(14,2),
    pr.inventory_usage_per_unit::NUMERIC(14,4)
FROM raw.products pr
JOIN analytics.dim_outlet o USING (outlet_id)
JOIN analytics.dim_property p USING (property_id)
ORDER BY pr.product_id;

INSERT INTO analytics.dim_supplier (
    supplier_id,
    supplier_name,
    category
)
SELECT supplier_id, supplier_name, category
FROM raw.suppliers
ORDER BY supplier_id;

INSERT INTO analytics.dim_department (
    department_id,
    department_name
)
SELECT department_id, department_name
FROM raw.departments
ORDER BY department_id;

INSERT INTO analytics.dim_room_segment (segment_name)
SELECT DISTINCT segment
FROM raw.pms_bookings_daily
ORDER BY segment;

INSERT INTO analytics.dim_channel (channel_name)
SELECT DISTINCT channel
FROM raw.pms_bookings_daily
ORDER BY channel;

INSERT INTO analytics.fact_room_inventory_daily (
    date_key,
    property_key,
    rooms_available
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    r.rooms_available::INTEGER
FROM raw.pms_inventory_daily r
JOIN analytics.dim_property p USING (property_id);

INSERT INTO analytics.fact_room_bookings_daily (
    date_key,
    property_key,
    segment_key,
    channel_key,
    rooms_sold,
    room_revenue
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    s.segment_key,
    c.channel_key,
    r.rooms_sold::INTEGER,
    r.room_revenue::NUMERIC(14,2)
FROM raw.pms_bookings_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_room_segment s ON s.segment_name = r.segment
JOIN analytics.dim_channel c ON c.channel_name = r.channel;

INSERT INTO analytics.fact_pos_outlet_daily (
    date_key,
    property_key,
    outlet_key,
    covers,
    gross_revenue,
    discount_amount,
    net_revenue
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    o.outlet_key,
    r.covers::INTEGER,
    r.gross_revenue::NUMERIC(14,2),
    r.discount_amount::NUMERIC(14,2),
    r.net_revenue::NUMERIC(14,2)
FROM raw.pos_checks_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_outlet o USING (outlet_id);

INSERT INTO analytics.fact_pos_product_daily (
    date_key,
    property_key,
    outlet_key,
    product_key,
    units_sold,
    net_revenue
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    o.outlet_key,
    pr.product_key,
    r.units_sold::INTEGER,
    r.net_revenue::NUMERIC(14,2)
FROM raw.pos_product_mix_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_outlet o USING (outlet_id)
JOIN analytics.dim_product pr USING (product_id);

INSERT INTO analytics.fact_purchases_daily (
    date_key,
    property_key,
    product_key,
    supplier_key,
    quantity,
    unit_cost,
    purchase_cost
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    pr.product_key,
    s.supplier_key,
    r.quantity::NUMERIC(14,2),
    r.unit_cost::NUMERIC(14,2),
    r.purchase_cost::NUMERIC(14,2)
FROM raw.purchases_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_product pr USING (product_id)
JOIN analytics.dim_supplier s USING (supplier_id);

INSERT INTO analytics.fact_inventory_daily (
    date_key,
    property_key,
    product_key,
    opening_qty,
    receipts_qty,
    usage_qty,
    waste_qty,
    closing_qty,
    weighted_unit_cost,
    inventory_value
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    pr.product_key,
    r.opening_qty::NUMERIC(14,2),
    r.receipts_qty::NUMERIC(14,2),
    r.usage_qty::NUMERIC(14,2),
    r.waste_qty::NUMERIC(14,2),
    r.closing_qty::NUMERIC(14,2),
    r.weighted_unit_cost::NUMERIC(14,2),
    r.inventory_value::NUMERIC(14,2)
FROM raw.inventory_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_product pr USING (product_id);

INSERT INTO analytics.fact_labour_daily (
    date_key,
    property_key,
    department_key,
    scheduled_hours,
    actual_hours,
    overtime_hours,
    labour_cost
)
SELECT
    TO_CHAR(r.date::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    d.department_key,
    r.scheduled_hours::NUMERIC(14,2),
    r.actual_hours::NUMERIC(14,2),
    r.overtime_hours::NUMERIC(14,2),
    r.labour_cost::NUMERIC(14,2)
FROM raw.labour_daily r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_department d USING (department_id);

INSERT INTO analytics.fact_budget_monthly (
    date_key,
    property_key,
    department_key,
    budget_revenue,
    budget_cost
)
SELECT
    TO_CHAR(r.month::DATE, 'YYYYMMDD')::INTEGER,
    p.property_key,
    d.department_key,
    r.budget_revenue::NUMERIC(14,2),
    r.budget_cost::NUMERIC(14,2)
FROM raw.budget_monthly r
JOIN analytics.dim_property p USING (property_id)
JOIN analytics.dim_department d USING (department_id);
