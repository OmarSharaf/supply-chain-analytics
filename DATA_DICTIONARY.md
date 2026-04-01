# Data Dictionary

## fact_orders / orders_cleaned.csv

| Column | Type | Description |
|--------|------|-------------|
| order_id | string | Unique order identifier (e.g. ORD00001) |
| order_date | date | Date the order was placed |
| supplier_id | string | FK to dim_suppliers |
| supplier_name | string | Supplier company name |
| product_id | string | FK to dim_products |
| product_name | string | Product description |
| product_category | string | Electronics / Components / Packaging / Raw Material / Logistics |
| warehouse_id | string | FK to dim_warehouses |
| warehouse_location | string | City and country of warehouse |
| quantity | int | Units ordered |
| unit_price | float | Price per unit (USD) |
| total_value | float | quantity × unit_price |
| shipping_cost | float | Freight cost for the order (USD) |
| total_order_cost | float | total_value + shipping_cost |
| shipping_mode | string | Air / Sea / Road / Rail |
| expected_lead_days | int | Contractual lead time |
| actual_lead_days | int | Actual days from order to delivery |
| on_time_delivery | int | 1 = delivered on or before expected date, 0 = late |
| delay_days | int | Max(0, actual_lead_days − expected_lead_days) |
| delay_category | string | On Time / 1-3 Days / 4-7 Days / 1-4 Weeks / >1 Month |
| order_status | string | Delivered / In Transit / Processing / Delayed / Cancelled |
| supplier_country | string | Country of supplier headquarters |
| year | int | Order year |
| month | int | Order month (1–12) |
| quarter | string | Q1 / Q2 / Q3 / Q4 |
| is_cancelled | int | 1 if order_status = Cancelled |
| is_delayed | int | 1 if delay_days > 0 |
| shipping_pct | float | shipping_cost / total_order_cost × 100 |

---

## supplier_kpis.csv

| Column | Type | Description |
|--------|------|-------------|
| supplier_id | string | Supplier identifier |
| supplier_name | string | Supplier company name |
| supplier_country | string | Country |
| total_orders | int | Total orders placed (excl. cancelled) |
| total_spend | float | Total spend with supplier (USD) |
| avg_order_value | float | Average order value |
| on_time_delivery_pct | float | % orders delivered on time |
| avg_delay_days | float | Average delay in days |
| delayed_orders | int | Count of delayed orders |
| total_quantity | int | Total units ordered |
| risk_score | float | 0–100 composite risk score |
| risk_category | string | High Risk / Medium Risk / Low Risk / Excellent |

---

## inventory_kpis.csv

| Column | Type | Description |
|--------|------|-------------|
| snapshot_date | date | Date of inventory snapshot |
| product_id | string | Product identifier |
| product_name | string | Product name |
| warehouse_id | string | Warehouse identifier |
| stock_level | int | Current units in stock |
| reorder_point | int | Trigger point for replenishment |
| eoq | int | Economic Order Quantity |
| unit_cost | float | Cost per unit |
| stock_value | float | stock_level × unit_cost |
| below_reorder | int | 1 if stock_level < reorder_point |
| days_of_supply | float | Estimated days until stockout |
| turnover_rate | float | Annualised inventory turnover ratio |
| stock_status | string | ⚠️ Below Reorder Point / 📦 Overstocked / ✅ Healthy |
