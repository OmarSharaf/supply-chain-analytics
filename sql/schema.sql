-- ============================================================
-- Supply Chain Analytics – Database Schema
-- Compatible with: PostgreSQL / SQLite / DuckDB
-- ============================================================

-- ── Dimension Tables ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_suppliers (
    supplier_id        VARCHAR(10)  PRIMARY KEY,
    supplier_name      VARCHAR(100) NOT NULL,
    country            VARCHAR(50),
    category           VARCHAR(50),
    reliability_score  DECIMAL(4,2),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id       VARCHAR(10)  PRIMARY KEY,
    product_name     VARCHAR(100) NOT NULL,
    category         VARCHAR(50),
    unit_cost        DECIMAL(10,2),
    lead_time_days   INT,
    reorder_point    INT,
    eoq              INT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_warehouses (
    warehouse_id  VARCHAR(10)  PRIMARY KEY,
    location      VARCHAR(100),
    capacity      INT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Fact Tables ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id             VARCHAR(10) PRIMARY KEY,
    order_date           DATE        NOT NULL,
    supplier_id          VARCHAR(10) REFERENCES dim_suppliers(supplier_id),
    product_id           VARCHAR(10) REFERENCES dim_products(product_id),
    warehouse_id         VARCHAR(10) REFERENCES dim_warehouses(warehouse_id),
    quantity             INT,
    unit_price           DECIMAL(10,2),
    total_value          DECIMAL(12,2),
    shipping_cost        DECIMAL(10,2),
    shipping_mode        VARCHAR(20),
    expected_lead_days   INT,
    actual_lead_days     INT,
    on_time_delivery     SMALLINT,   -- 1 = on time, 0 = late
    delay_days           INT,
    order_status         VARCHAR(20),
    year                 INT,
    month                INT,
    quarter              VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS fact_inventory (
    snapshot_id    SERIAL PRIMARY KEY,
    snapshot_date  DATE        NOT NULL,
    product_id     VARCHAR(10) REFERENCES dim_products(product_id),
    warehouse_id   VARCHAR(10) REFERENCES dim_warehouses(warehouse_id),
    stock_level    INT,
    reorder_point  INT,
    eoq            INT,
    unit_cost      DECIMAL(10,2),
    stock_value    DECIMAL(12,2),
    below_reorder  SMALLINT,
    days_of_supply DECIMAL(8,1),
    year           INT,
    month          INT
);

-- ── Indexes ───────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_date       ON fact_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_supplier   ON fact_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_orders_product    ON fact_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_inventory_date    ON fact_inventory(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON fact_inventory(product_id);
