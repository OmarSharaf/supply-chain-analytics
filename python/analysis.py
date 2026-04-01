"""
Supply Chain Analytics – Python Analysis & Charts
Generates publication-ready charts for the project README / Power BI supplement
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DOCS_DIR      = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0f1117",
    "axes.facecolor":    "#1a1d27",
    "axes.edgecolor":    "#2e3250",
    "axes.labelcolor":   "#c9d1d9",
    "text.color":        "#c9d1d9",
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "grid.color":        "#2e3250",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
})

PALETTE = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff"]


def load(filename: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROCESSED_DIR, filename))


def fmt_millions(x, _):
    return f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:.0f}K"


# ── Chart 1: Monthly Spend Trend ─────────────────────────────────────────────
def plot_monthly_spend(trends: pd.DataFrame):
    monthly = (
        trends.groupby(["year", "month"])["total_spend"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["label"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(range(len(monthly)), monthly["total_spend"], alpha=0.15, color=PALETTE[0])
    ax.plot(range(len(monthly)), monthly["total_spend"], color=PALETTE[0], linewidth=2.5, marker="o", markersize=3)

    ax.set_title("📈 Monthly Total Spend (2022–2024)", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spend")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.set_xticks(range(0, len(monthly), 3))
    ax.set_xticklabels(monthly["label"].iloc[::3], rotation=45, ha="right", fontsize=8)
    ax.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "monthly_spend_trend.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  📊 monthly_spend_trend.png")


# ── Chart 2: Supplier On-Time Delivery ───────────────────────────────────────
def plot_supplier_performance(kpis: pd.DataFrame):
    df = kpis.sort_values("on_time_delivery_pct", ascending=True).tail(8)

    colors = [PALETTE[2] if v < 80 else PALETTE[1] if v < 90 else PALETTE[0]
              for v in df["on_time_delivery_pct"]]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df["supplier_name"], df["on_time_delivery_pct"], color=colors, height=0.6)
    ax.axvline(90, color=PALETTE[0], linewidth=1.2, linestyle="--", label="Target (90%)")
    ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=9, color="#c9d1d9")
    ax.set_title("🏭 Supplier On-Time Delivery Performance", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("On-Time Delivery %")
    ax.set_xlim(0, 110)
    ax.legend()
    ax.grid(axis="x")
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "supplier_performance.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  📊 supplier_performance.png")


# ── Chart 3: Order Status Breakdown ──────────────────────────────────────────
def plot_order_status(orders: pd.DataFrame):
    counts = orders["order_status"].value_counts()

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(counts)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops={"linewidth": 2, "edgecolor": "#0f1117"},
    )
    for t in autotexts:
        t.set_color("#0f1117")
        t.set_fontweight("bold")

    ax.set_title("📦 Order Status Distribution", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "order_status_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  📊 order_status_distribution.png")


# ── Chart 4: Spend by Category ────────────────────────────────────────────────
def plot_spend_by_category(orders: pd.DataFrame):
    df = (
        orders[orders["order_status"] != "Cancelled"]
        .groupby("product_category")["total_value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(df["product_category"], df["total_value"], color=PALETTE[:len(df)], width=0.5)
    ax.bar_label(bars, fmt=lambda x: fmt_millions(x, None), padding=4, fontsize=9, color="#c9d1d9")
    ax.set_title("💰 Total Spend by Product Category", fontsize=14, fontweight="bold", pad=14)
    ax.set_ylabel("Total Spend")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "spend_by_category.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("  📊 spend_by_category.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("📊 Generating Analysis Charts...\n")
    orders = load("orders_cleaned.csv")
    kpis   = load("supplier_kpis.csv")
    trends = load("monthly_trends.csv")

    plot_monthly_spend(trends)
    plot_supplier_performance(kpis)
    plot_order_status(orders)
    plot_spend_by_category(orders)

    print(f"\n✅ All charts saved to: {DOCS_DIR}")


if __name__ == "__main__":
    main()
