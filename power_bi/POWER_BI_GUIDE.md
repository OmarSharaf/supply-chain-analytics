# Power BI Dashboard Guide

## 📥 Data Sources to Connect

Connect Power BI to the processed CSV files in `data/processed/`:

| File | Used For |
|------|----------|
| `orders_cleaned.csv` | Main orders fact table |
| `supplier_kpis.csv` | Supplier performance page |
| `monthly_trends.csv` | Trend analysis page |
| `inventory_kpis.csv` | Inventory health page |

---

## 📊 Recommended Dashboard Pages

### Page 1 – Executive Overview
| Visual | Fields |
|--------|--------|
| KPI Cards | Total Orders, Total Spend, On-Time %, Avg Lead Days |
| Line Chart | Monthly Spend Trend |
| Donut Chart | Order Status Distribution |
| Bar Chart | Spend by Product Category |

### Page 2 – Supplier Performance
| Visual | Fields |
|--------|--------|
| Table | Supplier Scorecard (on_time_pct, avg_delay_days, risk_category) |
| Bar Chart | Top Suppliers by On-Time Delivery % |
| Map | Supplier locations by country |
| Scatter | Total Spend vs On-Time % |

### Page 3 – Inventory Health
| Visual | Fields |
|--------|--------|
| KPI Card | Items Below Reorder Point |
| Bar Chart | Stock Level vs Reorder Point per Product |
| Table | Inventory Alerts (below_reorder = 1) |
| Gauge | Overall Inventory Health Score |

### Page 4 – Trend Analysis
| Visual | Fields |
|--------|--------|
| Area Chart | Monthly Spend by Category |
| Line Chart | On-Time Delivery % over Time |
| Bar Chart | QoQ Order Volume |
| Slicer | Year / Quarter / Category |

---

## 🎨 Recommended Theme Colors

```json
{
  "name": "Supply Chain Dark",
  "dataColors": ["#58a6ff","#3fb950","#f78166","#d2a8ff","#ffa657","#79c0ff"],
  "background": "#0f1117",
  "foreground": "#c9d1d9",
  "tableAccent": "#58a6ff"
}
```

---

## 🔢 DAX Measures to Create

```dax
-- On-Time Delivery %
On_Time_Pct =
DIVIDE(
    CALCULATE(COUNTROWS(orders_cleaned), orders_cleaned[on_time_delivery] = 1),
    COUNTROWS(orders_cleaned)
) * 100

-- Total Spend (excl. cancelled)
Total_Spend =
CALCULATE(
    SUM(orders_cleaned[total_order_cost]),
    orders_cleaned[order_status] <> "Cancelled"
)

-- Avg Lead Days
Avg_Lead_Days =
AVERAGE(orders_cleaned[actual_lead_days])

-- Supplier Risk Score
Risk_Score =
AVERAGEX(
    supplier_kpis,
    supplier_kpis[on_time_delivery_pct] * 0.6 +
    (1 - supplier_kpis[avg_delay_days] / MAXX(supplier_kpis, supplier_kpis[avg_delay_days])) * 40
)
```
