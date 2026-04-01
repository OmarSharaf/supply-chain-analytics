"""
Supply Chain ETL Pipeline
Cleans, transforms, and enriches raw supply chain data
"""

import pandas as pd
import numpy as np
import os

RAW_DIR       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ── Loaders ───────────────────────────────────────────────────────────────────
def load_raw(filename: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)
    print(f"  📥 Loaded {filename:<22} → {len(df):,} rows")
    return df


# ── Transformations ───────────────────────────────────────────────────────────
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Remove cancelled orders for KPI calculations
    df["is_cancelled"] = (df["order_status"] == "Cancelled").astype(int)

    # Cost metrics
    df["total_order_cost"] = df["total_value"] + df["shipping_cost"]
    df["shipping_pct"]     = (df["shipping_cost"] / df["total_order_cost"] * 100).round(2)

    # Performance flags
    df["is_delayed"]        = (df["delay_days"] > 0).astype(int)
    df["delay_category"]    = pd.cut(
        df["delay_days"],
        bins=[-1, 0, 3, 7, 30, 9999],
        labels=["On Time", "1-3 Days", "4-7 Days", "1-4 Weeks", ">1 Month"]
    )

    return df


def build_supplier_kpis(orders: pd.DataFrame) -> pd.DataFrame:
    active = orders[orders["order_status"] != "Cancelled"]

    kpis = active.groupby(["supplier_id", "supplier_name", "supplier_country"]).agg(
        total_orders        = ("order_id",          "count"),
        total_spend         = ("total_order_cost",  "sum"),
        avg_order_value     = ("total_value",        "mean"),
        on_time_delivery_pct= ("on_time_delivery",  "mean"),
        avg_delay_days      = ("delay_days",         "mean"),
        delayed_orders      = ("is_delayed",         "sum"),
        total_quantity      = ("quantity",            "sum"),
    ).reset_index()

    kpis["on_time_delivery_pct"] = (kpis["on_time_delivery_pct"] * 100).round(2)
    kpis["avg_delay_days"]       = kpis["avg_delay_days"].round(2)
    kpis["avg_order_value"]      = kpis["avg_order_value"].round(2)
    kpis["total_spend"]          = kpis["total_spend"].round(2)

    # Risk score (0–100, lower = riskier)
    kpis["risk_score"] = (
        kpis["on_time_delivery_pct"] * 0.6 +
        (1 - kpis["avg_delay_days"] / kpis["avg_delay_days"].max()) * 40
    ).round(2)

    kpis["risk_category"] = pd.cut(
        kpis["risk_score"],
        bins=[0, 60, 75, 90, 101],
        labels=["High Risk", "Medium Risk", "Low Risk", "Excellent"]
    )

    return kpis


def build_monthly_trends(orders: pd.DataFrame) -> pd.DataFrame:
    active = orders[orders["order_status"] != "Cancelled"].copy()
    active["month_year"] = active["order_date"].dt.to_period("M").astype(str)

    trends = active.groupby(["year", "month", "month_year", "product_category"]).agg(
        total_orders    = ("order_id",         "count"),
        total_spend     = ("total_order_cost", "sum"),
        total_quantity  = ("quantity",          "sum"),
        on_time_pct     = ("on_time_delivery", "mean"),
        avg_lead_days   = ("actual_lead_days", "mean"),
    ).reset_index()

    trends["on_time_pct"]   = (trends["on_time_pct"] * 100).round(2)
    trends["avg_lead_days"] = trends["avg_lead_days"].round(2)
    trends["total_spend"]   = trends["total_spend"].round(2)

    # Month-over-month spend growth
    trends = trends.sort_values(["product_category", "year", "month"])
    trends["spend_mom_growth"] = (
        trends.groupby("product_category")["total_spend"].pct_change() * 100
    ).round(2)

    return trends


def build_inventory_kpis(inventory: pd.DataFrame) -> pd.DataFrame:
    inv = inventory.copy()
    inv["snapshot_date"] = pd.to_datetime(inv["snapshot_date"])

    # Latest snapshot per product & warehouse
    latest = inv.sort_values("snapshot_date").groupby(
        ["product_id", "warehouse_id"]
    ).last().reset_index()

    # Inventory turnover proxy (annualised)
    latest["turnover_rate"] = (
        latest["reorder_point"] * 12 / latest["stock_level"].replace(0, 1)
    ).round(2)

    latest["stock_status"] = np.where(
        latest["stock_level"] < latest["reorder_point"],
        "⚠️ Below Reorder Point",
        np.where(
            latest["stock_level"] > latest["eoq"] * 1.5,
            "📦 Overstocked",
            "✅ Healthy"
        )
    )

    return latest


# ── Saver ─────────────────────────────────────────────────────────────────────
def save(df: pd.DataFrame, filename: str):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  💾 Saved  {filename:<30} → {len(df):,} rows")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("🔄 Running ETL Pipeline...\n")

    # Load
    orders    = load_raw("orders.csv")
    inventory = load_raw("inventory.csv")
    print()

    # Transform & save
    orders_clean = clean_orders(orders)
    save(orders_clean,               "orders_cleaned.csv")
    save(build_supplier_kpis(orders_clean), "supplier_kpis.csv")
    save(build_monthly_trends(orders_clean),"monthly_trends.csv")
    save(build_inventory_kpis(inventory),   "inventory_kpis.csv")

    print("\n✅ ETL Pipeline completed successfully!")


if __name__ == "__main__":
    main()
