CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.properties (
    property_id TEXT NOT NULL,
    property_name TEXT NOT NULL,
    archetype TEXT NOT NULL,
    rooms_count TEXT NOT NULL,
    city TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.outlets (
    outlet_id TEXT NOT NULL,
    property_id TEXT NOT NULL,
    outlet_name TEXT NOT NULL,
    outlet_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id TEXT NOT NULL,
    outlet_id TEXT NOT NULL,
    property_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    menu_price TEXT NOT NULL,
    standard_unit_cost TEXT NOT NULL,
    inventory_usage_per_unit TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.suppliers (
    supplier_id TEXT NOT NULL,
    supplier_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.departments (
    department_id TEXT NOT NULL,
    department_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.pms_inventory_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    rooms_available TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.pms_bookings_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    segment TEXT NOT NULL,
    channel TEXT NOT NULL,
    rooms_sold TEXT NOT NULL,
    room_revenue TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.pos_checks_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    outlet_id TEXT NOT NULL,
    covers TEXT NOT NULL,
    gross_revenue TEXT NOT NULL,
    discount_amount TEXT NOT NULL,
    net_revenue TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.pos_product_mix_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    outlet_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    units_sold TEXT NOT NULL,
    net_revenue TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.purchases_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    quantity TEXT NOT NULL,
    unit_cost TEXT NOT NULL,
    purchase_cost TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.inventory_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    opening_qty TEXT NOT NULL,
    receipts_qty TEXT NOT NULL,
    usage_qty TEXT NOT NULL,
    waste_qty TEXT NOT NULL,
    closing_qty TEXT NOT NULL,
    weighted_unit_cost TEXT NOT NULL,
    inventory_value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.labour_daily (
    date TEXT NOT NULL,
    property_id TEXT NOT NULL,
    department_id TEXT NOT NULL,
    scheduled_hours TEXT NOT NULL,
    actual_hours TEXT NOT NULL,
    overtime_hours TEXT NOT NULL,
    labour_cost TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.budget_monthly (
    month TEXT NOT NULL,
    property_id TEXT NOT NULL,
    department_id TEXT NOT NULL,
    budget_revenue TEXT NOT NULL,
    budget_cost TEXT NOT NULL
);
