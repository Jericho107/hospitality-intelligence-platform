CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year_number INTEGER NOT NULL,
    month_number INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    month_start DATE NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_property (
    property_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    property_id TEXT NOT NULL UNIQUE,
    property_name TEXT NOT NULL,
    archetype TEXT NOT NULL,
    rooms_count INTEGER NOT NULL CHECK (rooms_count > 0),
    city TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_outlet (
    outlet_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    outlet_id TEXT NOT NULL UNIQUE,
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    outlet_name TEXT NOT NULL,
    outlet_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    outlet_key BIGINT NOT NULL REFERENCES analytics.dim_outlet(outlet_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    menu_price NUMERIC(14,2) NOT NULL CHECK (menu_price > 0),
    standard_unit_cost NUMERIC(14,2) NOT NULL CHECK (standard_unit_cost > 0),
    inventory_usage_per_unit NUMERIC(14,4) NOT NULL CHECK (inventory_usage_per_unit > 0)
);

CREATE TABLE IF NOT EXISTS analytics.dim_supplier (
    supplier_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id TEXT NOT NULL UNIQUE,
    supplier_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_department (
    department_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_id TEXT NOT NULL UNIQUE,
    department_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_room_segment (
    segment_key SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    segment_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.dim_channel (
    channel_key SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    channel_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.fact_room_inventory_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    rooms_available INTEGER NOT NULL CHECK (rooms_available > 0),
    PRIMARY KEY (date_key, property_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_room_bookings_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    segment_key SMALLINT NOT NULL REFERENCES analytics.dim_room_segment(segment_key),
    channel_key SMALLINT NOT NULL REFERENCES analytics.dim_channel(channel_key),
    rooms_sold INTEGER NOT NULL CHECK (rooms_sold >= 0),
    room_revenue NUMERIC(14,2) NOT NULL CHECK (room_revenue >= 0),
    PRIMARY KEY (date_key, property_key, segment_key, channel_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_pos_outlet_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    outlet_key BIGINT NOT NULL REFERENCES analytics.dim_outlet(outlet_key),
    covers INTEGER NOT NULL CHECK (covers >= 0),
    gross_revenue NUMERIC(14,2) NOT NULL CHECK (gross_revenue >= 0),
    discount_amount NUMERIC(14,2) NOT NULL CHECK (discount_amount >= 0),
    net_revenue NUMERIC(14,2) NOT NULL CHECK (net_revenue >= 0),
    PRIMARY KEY (date_key, property_key, outlet_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_pos_product_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    outlet_key BIGINT NOT NULL REFERENCES analytics.dim_outlet(outlet_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
    net_revenue NUMERIC(14,2) NOT NULL CHECK (net_revenue >= 0),
    PRIMARY KEY (date_key, property_key, outlet_key, product_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_purchases_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    supplier_key BIGINT NOT NULL REFERENCES analytics.dim_supplier(supplier_key),
    quantity NUMERIC(14,2) NOT NULL CHECK (quantity >= 0),
    unit_cost NUMERIC(14,2) NOT NULL CHECK (unit_cost > 0),
    purchase_cost NUMERIC(14,2) NOT NULL CHECK (purchase_cost >= 0),
    PRIMARY KEY (date_key, property_key, product_key, supplier_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_inventory_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    opening_qty NUMERIC(14,2) NOT NULL CHECK (opening_qty >= 0),
    receipts_qty NUMERIC(14,2) NOT NULL CHECK (receipts_qty >= 0),
    usage_qty NUMERIC(14,2) NOT NULL CHECK (usage_qty >= 0),
    waste_qty NUMERIC(14,2) NOT NULL CHECK (waste_qty >= 0),
    closing_qty NUMERIC(14,2) NOT NULL CHECK (closing_qty >= 0),
    weighted_unit_cost NUMERIC(14,2) NOT NULL CHECK (weighted_unit_cost > 0),
    inventory_value NUMERIC(14,2) NOT NULL CHECK (inventory_value >= 0),
    PRIMARY KEY (date_key, property_key, product_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_labour_daily (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    department_key BIGINT NOT NULL REFERENCES analytics.dim_department(department_key),
    scheduled_hours NUMERIC(14,2) NOT NULL CHECK (scheduled_hours >= 0),
    actual_hours NUMERIC(14,2) NOT NULL CHECK (actual_hours >= 0),
    overtime_hours NUMERIC(14,2) NOT NULL CHECK (overtime_hours >= 0),
    labour_cost NUMERIC(14,2) NOT NULL CHECK (labour_cost >= 0),
    PRIMARY KEY (date_key, property_key, department_key)
);

CREATE TABLE IF NOT EXISTS analytics.fact_budget_monthly (
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    property_key BIGINT NOT NULL REFERENCES analytics.dim_property(property_key),
    department_key BIGINT NOT NULL REFERENCES analytics.dim_department(department_key),
    budget_revenue NUMERIC(14,2) NOT NULL CHECK (budget_revenue >= 0),
    budget_cost NUMERIC(14,2) NOT NULL CHECK (budget_cost >= 0),
    PRIMARY KEY (date_key, property_key, department_key)
);
