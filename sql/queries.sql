-- ============================================================
-- Supply Chain Analytics – Core KPI Queries
-- ============================================================


-- ── 1. Overall Supply Chain Health Summary ────────────────
SELECT
    COUNT(*)                                          AS total_orders,
    SUM(total_value)                                  AS total_spend,
    ROUND(AVG(on_time_delivery) * 100, 2)             AS on_time_delivery_pct,
    ROUND(AVG(actual_lead_days), 1)                   AS avg_lead_days,
    ROUND(AVG(delay_days), 1)                         AS avg_delay_days,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2)                                                AS cancellation_rate_pct
FROM fact_orders;


-- ── 2. Supplier Performance Scorecard ────────────────────
SELECT
    s.supplier_name,
    s.country,
    s.category,
    COUNT(o.order_id)                                 AS total_orders,
    ROUND(SUM(o.total_value), 0)                      AS total_spend,
    ROUND(AVG(o.on_time_delivery) * 100, 2)           AS on_time_pct,
    ROUND(AVG(o.delay_days), 2)                       AS avg_delay_days,
    SUM(o.delay_days)                                 AS total_delay_days,
    ROUND(AVG(o.actual_lead_days), 1)                 AS avg_lead_days,
    CASE
        WHEN AVG(o.on_time_delivery) >= 0.90 THEN '🟢 Excellent'
        WHEN AVG(o.on_time_delivery) >= 0.75 THEN '🟡 Acceptable'
        ELSE '🔴 At Risk'
    END                                               AS performance_tier
FROM fact_orders o
JOIN dim_suppliers s ON o.supplier_id = s.supplier_id
WHERE o.order_status != 'Cancelled'
GROUP BY s.supplier_id, s.supplier_name, s.country, s.category
ORDER BY on_time_pct DESC;


-- ── 3. Monthly Spend & Order Trend ───────────────────────
SELECT
    o.year,
    o.month,
    o.quarter,
    COUNT(o.order_id)                                 AS order_count,
    ROUND(SUM(o.total_value), 0)                      AS total_spend,
    ROUND(SUM(o.shipping_cost), 0)                    AS shipping_spend,
    ROUND(AVG(o.unit_price), 2)                       AS avg_unit_price,
    ROUND(AVG(o.on_time_delivery) * 100, 2)           AS on_time_pct
FROM fact_orders o
WHERE o.order_status != 'Cancelled'
GROUP BY o.year, o.month, o.quarter
ORDER BY o.year, o.month;


-- ── 4. Inventory Alerts – Below Reorder Point ────────────
SELECT
    p.product_name,
    p.category,
    w.location                                        AS warehouse,
    i.stock_level,
    i.reorder_point,
    i.reorder_point - i.stock_level                   AS units_short,
    i.days_of_supply,
    i.stock_value,
    CASE
        WHEN i.stock_level = 0               THEN '🚨 Stockout'
        WHEN i.stock_level < i.reorder_point THEN '⚠️  Below Reorder'
        ELSE '✅ OK'
    END                                               AS stock_alert
FROM fact_inventory i
JOIN dim_products  p ON i.product_id  = p.product_id
JOIN dim_warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.snapshot_date = (SELECT MAX(snapshot_date) FROM fact_inventory)
  AND i.below_reorder = 1
ORDER BY units_short DESC;


-- ── 5. Top 10 Products by Total Spend ────────────────────
SELECT
    p.product_name,
    p.category,
    SUM(o.quantity)                                   AS total_units_ordered,
    ROUND(SUM(o.total_value), 0)                      AS total_spend,
    ROUND(AVG(o.unit_price), 2)                       AS avg_unit_price,
    COUNT(DISTINCT o.supplier_id)                     AS num_suppliers,
    ROUND(AVG(o.on_time_delivery) * 100, 2)           AS on_time_pct
FROM fact_orders o
JOIN dim_products p ON o.product_id = p.product_id
WHERE o.order_status != 'Cancelled'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_spend DESC
LIMIT 10;


-- ── 6. Shipping Mode Cost Analysis ───────────────────────
SELECT
    shipping_mode,
    COUNT(*)                                          AS order_count,
    ROUND(AVG(shipping_cost), 2)                      AS avg_shipping_cost,
    ROUND(SUM(shipping_cost), 0)                      AS total_shipping_cost,
    ROUND(AVG(actual_lead_days), 1)                   AS avg_lead_days,
    ROUND(AVG(on_time_delivery) * 100, 2)             AS on_time_pct
FROM fact_orders
WHERE order_status != 'Cancelled'
GROUP BY shipping_mode
ORDER BY avg_shipping_cost DESC;


-- ── 7. Quarter-over-Quarter Performance ──────────────────
SELECT
    year,
    quarter,
    COUNT(*)                                          AS orders,
    ROUND(SUM(total_value), 0)                        AS revenue,
    ROUND(AVG(on_time_delivery) * 100, 2)             AS on_time_pct,
    ROUND(AVG(actual_lead_days), 1)                   AS avg_lead_days
FROM fact_orders
WHERE order_status != 'Cancelled'
GROUP BY year, quarter
ORDER BY year, quarter;


-- ── 8. Supplier Dependency Risk (Single-Source Products) ──
SELECT
    p.product_name,
    COUNT(DISTINCT o.supplier_id)                     AS supplier_count,
    CASE
        WHEN COUNT(DISTINCT o.supplier_id) = 1 THEN '🔴 Single Source Risk'
        WHEN COUNT(DISTINCT o.supplier_id) = 2 THEN '🟡 Limited Sourcing'
        ELSE '🟢 Diversified'
    END                                               AS sourcing_risk
FROM fact_orders o
JOIN dim_products p ON o.product_id = p.product_id
WHERE o.order_status != 'Cancelled'
GROUP BY p.product_id, p.product_name
ORDER BY supplier_count ASC;
