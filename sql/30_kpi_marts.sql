CREATE TABLE IF NOT EXISTS analytics.kpi_rooms_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    rooms_available INTEGER NOT NULL,
    rooms_sold INTEGER NOT NULL,
    room_revenue NUMERIC(16,2) NOT NULL,
    occupancy_pct NUMERIC(12,8) NOT NULL,
    adr NUMERIC(16,6),
    revpar NUMERIC(16,6) NOT NULL,
    PRIMARY KEY (date_key, property_key)
);

CREATE TABLE IF NOT EXISTS analytics.kpi_fnb_outlet_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    outlet_key BIGINT NOT NULL REFERENCES analytics.dim_outlet(outlet_key),
    covers INTEGER NOT NULL,
    gross_revenue NUMERIC(16,2) NOT NULL,
    discount_amount NUMERIC(16,2) NOT NULL,
    net_revenue NUMERIC(16,2) NOT NULL,
    average_check NUMERIC(16,6),
    discount_rate NUMERIC(12,8),
    PRIMARY KEY (date_key, property_key, outlet_key)
);

CREATE TABLE IF NOT EXISTS analytics.kpi_purchasing_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    supplier_key BIGINT NOT NULL REFERENCES analytics.dim_supplier(supplier_key),
    quantity NUMERIC(16,2) NOT NULL,
    actual_purchase_cost NUMERIC(16,2) NOT NULL,
    standard_purchase_cost NUMERIC(16,4) NOT NULL,
    purchase_price_variance NUMERIC(16,4) NOT NULL,
    PRIMARY KEY (date_key, property_key, product_key, supplier_key)
);

CREATE TABLE IF NOT EXISTS analytics.kpi_inventory_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    usage_qty NUMERIC(16,2) NOT NULL,
    waste_qty NUMERIC(16,2) NOT NULL,
    weighted_unit_cost NUMERIC(16,2) NOT NULL,
    usage_cost NUMERIC(16,4) NOT NULL,
    waste_cost NUMERIC(16,4) NOT NULL,
    waste_pct NUMERIC(12,8),
    PRIMARY KEY (date_key, property_key, product_key)
);

CREATE TABLE IF NOT EXISTS analytics.kpi_labour_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    department_key BIGINT NOT NULL REFERENCES analytics.dim_department(department_key),
    actual_hours NUMERIC(16,2) NOT NULL,
    overtime_hours NUMERIC(16,2) NOT NULL,
    labour_cost NUMERIC(16,2) NOT NULL,
    labour_cost_per_hour NUMERIC(16,6),
    overtime_share NUMERIC(12,8),
    PRIMARY KEY (date_key, property_key, department_key)
);

TRUNCATE TABLE
    analytics.kpi_labour_daily,
    analytics.kpi_inventory_daily,
    analytics.kpi_purchasing_daily,
    analytics.kpi_fnb_outlet_daily,
    analytics.kpi_rooms_daily;

INSERT INTO analytics.kpi_rooms_daily (
    date_key,
    property_key,
    rooms_available,
    rooms_sold,
    room_revenue,
    occupancy_pct,
    adr,
    revpar
)
SELECT
    i.date_key,
    i.property_key,
    i.rooms_available,
    COALESCE(SUM(b.rooms_sold), 0)::INTEGER AS rooms_sold,
    COALESCE(SUM(b.room_revenue), 0)::NUMERIC(16,2) AS room_revenue,
    (
        COALESCE(SUM(b.rooms_sold), 0)::NUMERIC
        / i.rooms_available::NUMERIC
    )::NUMERIC(12,8) AS occupancy_pct,
    CASE
        WHEN COALESCE(SUM(b.rooms_sold), 0) = 0 THEN NULL
        ELSE (
            COALESCE(SUM(b.room_revenue), 0)::NUMERIC
            / SUM(b.rooms_sold)::NUMERIC
        )::NUMERIC(16,6)
    END AS adr,
    (
        COALESCE(SUM(b.room_revenue), 0)::NUMERIC
        / i.rooms_available::NUMERIC
    )::NUMERIC(16,6) AS revpar
FROM analytics.fact_room_inventory_daily i
LEFT JOIN analytics.fact_room_bookings_daily b
    ON b.date_key = i.date_key
   AND b.property_key = i.property_key
GROUP BY i.date_key, i.property_key, i.rooms_available;

INSERT INTO analytics.kpi_fnb_outlet_daily (
    date_key,
    property_key,
    outlet_key,
    covers,
    gross_revenue,
    discount_amount,
    net_revenue,
    average_check,
    discount_rate
)
SELECT
    date_key,
    property_key,
    outlet_key,
    covers,
    gross_revenue,
    discount_amount,
    net_revenue,
    CASE
        WHEN covers = 0 THEN NULL
        ELSE (net_revenue / covers::NUMERIC)::NUMERIC(16,6)
    END,
    CASE
        WHEN gross_revenue = 0 THEN NULL
        ELSE (discount_amount / gross_revenue)::NUMERIC(12,8)
    END
FROM analytics.fact_pos_outlet_daily;

INSERT INTO analytics.kpi_purchasing_daily (
    date_key,
    property_key,
    product_key,
    supplier_key,
    quantity,
    actual_purchase_cost,
    standard_purchase_cost,
    purchase_price_variance
)
SELECT
    f.date_key,
    f.property_key,
    f.product_key,
    f.supplier_key,
    f.quantity,
    f.purchase_cost,
    (f.quantity * p.standard_unit_cost)::NUMERIC(16,4),
    (f.purchase_cost - (f.quantity * p.standard_unit_cost))::NUMERIC(16,4)
FROM analytics.fact_purchases_daily f
JOIN analytics.dim_product p ON p.product_key = f.product_key;

INSERT INTO analytics.kpi_inventory_daily (
    date_key,
    property_key,
    product_key,
    usage_qty,
    waste_qty,
    weighted_unit_cost,
    usage_cost,
    waste_cost,
    waste_pct
)
SELECT
    date_key,
    property_key,
    product_key,
    usage_qty,
    waste_qty,
    weighted_unit_cost,
    (usage_qty * weighted_unit_cost)::NUMERIC(16,4),
    (waste_qty * weighted_unit_cost)::NUMERIC(16,4),
    CASE
        WHEN usage_qty + waste_qty = 0 THEN NULL
        ELSE (waste_qty / (usage_qty + waste_qty))::NUMERIC(12,8)
    END
FROM analytics.fact_inventory_daily;

INSERT INTO analytics.kpi_labour_daily (
    date_key,
    property_key,
    department_key,
    actual_hours,
    overtime_hours,
    labour_cost,
    labour_cost_per_hour,
    overtime_share
)
SELECT
    date_key,
    property_key,
    department_key,
    actual_hours,
    overtime_hours,
    labour_cost,
    CASE
        WHEN actual_hours = 0 THEN NULL
        ELSE (labour_cost / actual_hours)::NUMERIC(16,6)
    END,
    CASE
        WHEN actual_hours = 0 THEN NULL
        ELSE (overtime_hours / actual_hours)::NUMERIC(12,8)
    END
FROM analytics.fact_labour_daily;
