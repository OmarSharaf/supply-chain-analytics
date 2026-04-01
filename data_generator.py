"""
Supply Chain Synthetic Data Generator
Generates realistic supply chain data for analytics and visualization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ── Seeds for reproducibility ────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_ORDERS   = 5000

# ── Reference Data ────────────────────────────────────────────────────────────
SUPPLIERS = [
    {"supplier_id": "SUP001", "name": "AlphaTech Manufacturing",  "country": "China",   "category": "Electronics", "reliability_score": 0.92},
    {"supplier_id": "SUP002", "name": "BetaLogistics GmbH",       "country": "Germany", "category": "Logistics",   "reliability_score": 0.88},
    {"supplier_id": "SUP003", "name": "Gamma Parts Co.",           "country": "USA",     "category": "Components",  "reliability_score": 0.95},
    {"supplier_id": "SUP004", "name": "Delta Raw Materials Ltd",   "country": "Brazil",  "category": "Raw Material","reliability_score": 0.78},
    {"supplier_id": "SUP005", "name": "Epsilon Packaging Inc.",    "country": "India",   "category": "Packaging",   "reliability_score": 0.85},
    {"supplier_id": "SUP006", "name": "Zeta Electronics Corp.",    "country": "Japan",   "category": "Electronics", "reliability_score": 0.97},
    {"supplier_id": "SUP007", "name": "Eta Industrial Supplies",   "country": "Mexico",  "category": "Components",  "reliability_score": 0.80},
    {"supplier_id": "SUP008", "name": "Theta Freight Solutions",   "country": "UK",      "category": "Logistics",   "reliability_score": 0.91},
]

PRODUCTS = [
    {"product_id": "PRD001", "name": "Microcontroller Unit",  "category": "Electronics", "unit_cost": 45.00,  "lead_time_days": 30, "reorder_point": 200, "eoq": 500},
    {"product_id": "PRD002", "name": "Steel Frame Assembly",  "category": "Components",  "unit_cost": 120.00, "lead_time_days": 14, "reorder_point": 100, "eoq": 250},
    {"product_id": "PRD003", "name": "Polymer Casing",        "category": "Packaging",   "unit_cost": 8.50,   "lead_time_days": 7,  "reorder_point": 500, "eoq": 1000},
    {"product_id": "PRD004", "name": "Lithium Battery Pack",  "category": "Electronics", "unit_cost": 85.00,  "lead_time_days": 21, "reorder_point": 150, "eoq": 300},
    {"product_id": "PRD005", "name": "Copper Wiring Bundle",  "category": "Raw Material","unit_cost": 32.00,  "lead_time_days": 10, "reorder_point": 300, "eoq": 600},
    {"product_id": "PRD006", "name": "Sensor Module",         "category": "Electronics", "unit_cost": 55.00,  "lead_time_days": 25, "reorder_point": 120, "eoq": 400},
    {"product_id": "PRD007", "name": "Aluminum Housing",      "category": "Components",  "unit_cost": 95.00,  "lead_time_days": 12, "reorder_point": 80,  "eoq": 200},
    {"product_id": "PRD008", "name": "Rubber Seal Kit",       "category": "Raw Material","unit_cost": 5.00,   "lead_time_days": 5,  "reorder_point": 1000,"eoq": 2000},
]

WAREHOUSES = [
    {"warehouse_id": "WH001", "location": "New York, USA",      "capacity": 10000},
    {"warehouse_id": "WH002", "location": "Shanghai, China",    "capacity": 15000},
    {"warehouse_id": "WH003", "location": "Frankfurt, Germany", "capacity": 8000},
    {"warehouse_id": "WH004", "location": "Dubai, UAE",         "capacity": 12000},
]

SHIPPING_MODES = ["Air", "Sea", "Road", "Rail"]
ORDER_STATUSES = ["Delivered", "In Transit", "Processing", "Delayed", "Cancelled"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def random_date(start: datetime, end: datetime) -> datetime:
    return start + timedelta(days=random.randint(0, (end - start).days))

def weighted_status(reliability: float) -> str:
    if random.random() < reliability:
        return random.choices(["Delivered", "In Transit"], weights=[0.85, 0.15])[0]
    return random.choices(["Delayed", "Processing", "Cancelled"], weights=[0.6, 0.3, 0.1])[0]

# ── Generators ────────────────────────────────────────────────────────────────
def generate_suppliers() -> pd.DataFrame:
    return pd.DataFrame(SUPPLIERS)

def generate_products() -> pd.DataFrame:
    return pd.DataFrame(PRODUCTS)

def generate_warehouses() -> pd.DataFrame:
    return pd.DataFrame(WAREHOUSES)

def generate_orders() -> pd.DataFrame:
    sup_df  = pd.DataFrame(SUPPLIERS)
    prod_df = pd.DataFrame(PRODUCTS)
    rows = []

    for i in range(N_ORDERS):
        supplier = sup_df.sample(1).iloc[0]
        product  = prod_df.sample(1).iloc[0]
        wh       = random.choice(WAREHOUSES)

        order_date    = random_date(START_DATE, END_DATE)
        expected_days = int(product["lead_time_days"] * np.random.uniform(0.8, 1.5))
        actual_days   = int(expected_days * np.random.uniform(0.7, 1.8))
        status        = weighted_status(supplier["reliability_score"])
        quantity      = int(np.random.lognormal(mean=4.5, sigma=0.8))
        unit_price    = product["unit_cost"] * np.random.uniform(1.05, 1.35)
        shipping_cost = quantity * np.random.uniform(0.5, 3.0)

        rows.append({
            "order_id":           f"ORD{str(i+1).zfill(5)}",
            "order_date":         order_date.strftime("%Y-%m-%d"),
            "supplier_id":        supplier["supplier_id"],
            "supplier_name":      supplier["name"],
            "product_id":         product["product_id"],
            "product_name":       product["name"],
            "product_category":   product["category"],
            "warehouse_id":       wh["warehouse_id"],
            "warehouse_location": wh["location"],
            "quantity":           quantity,
            "unit_price":         round(unit_price, 2),
            "total_value":        round(quantity * unit_price, 2),
            "shipping_cost":      round(shipping_cost, 2),
            "shipping_mode":      random.choice(SHIPPING_MODES),
            "expected_lead_days": expected_days,
            "actual_lead_days":   actual_days,
            "on_time_delivery":   1 if actual_days <= expected_days else 0,
            "delay_days":         max(0, actual_days - expected_days),
            "order_status":       status,
            "supplier_country":   supplier["country"],
            "year":               order_date.year,
            "month":              order_date.month,
            "quarter":            f"Q{(order_date.month - 1) // 3 + 1}",
        })

    return pd.DataFrame(rows)

def generate_inventory() -> pd.DataFrame:
    rows = []
    for prod in PRODUCTS:
        for wh in WAREHOUSES:
            for month_offset in range(36):          # 3 years monthly snapshots
                snap_date = START_DATE + timedelta(days=30 * month_offset)
                stock = int(np.random.uniform(
                    prod["reorder_point"] * 0.5,
                    prod["eoq"] * 2
                ))
                rows.append({
                    "snapshot_date":  snap_date.strftime("%Y-%m-%d"),
                    "product_id":     prod["product_id"],
                    "product_name":   prod["name"],
                    "warehouse_id":   wh["warehouse_id"],
                    "stock_level":    stock,
                    "reorder_point":  prod["reorder_point"],
                    "eoq":            prod["eoq"],
                    "unit_cost":      prod["unit_cost"],
                    "stock_value":    round(stock * prod["unit_cost"], 2),
                    "below_reorder":  1 if stock < prod["reorder_point"] else 0,
                    "days_of_supply": round(stock / max(prod["reorder_point"] / 30, 1), 1),
                    "year":           snap_date.year,
                    "month":          snap_date.month,
                })
    return pd.DataFrame(rows)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("🚀 Generating Supply Chain Data...")

    dfs = {
        "suppliers.csv":  generate_suppliers(),
        "products.csv":   generate_products(),
        "warehouses.csv": generate_warehouses(),
        "orders.csv":     generate_orders(),
        "inventory.csv":  generate_inventory(),
    }

    for filename, df in dfs.items():
        path = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(path, index=False)
        print(f"  ✅ {filename:<22} → {len(df):,} rows")

    print("\n✅ All data generated successfully!")
    print(f"   Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
