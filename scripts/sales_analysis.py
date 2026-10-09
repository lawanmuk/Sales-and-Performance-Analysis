"""Sales performance analysis for the Superstore dataset.

Run from anywhere:
    python scripts/sales_analysis.py            # save charts and show them
    python scripts/sales_analysis.py --no-show  # save charts only
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import plotly.express as px
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "train.csv"
VISUALS_DIR = BASE_DIR / "visuals"

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOLLARS = mticker.StrMethodFormatter("${x:,.0f}")


def load_data(path: Path) -> pd.DataFrame:
    """Load the CSV, parse dates and add Year and Month columns."""
    df = pd.read_csv(path)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month  # 1 to 12, so months sort correctly
    return df


def plot_sales_by_category(df: pd.DataFrame, show: bool) -> None:
    sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    sales.plot(kind="bar", color=["skyblue", "orange", "green"], ax=ax)
    ax.set_title("Total Sales by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Sales")
    ax.yaxis.set_major_formatter(DOLLARS)
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "sales_by_category.png", dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def plot_monthly_sales(df: pd.DataFrame, show: bool) -> None:
    monthly = df.groupby(["Year", "Month"])["Sales"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly, x="Month", y="Sales", hue="Year",
                 palette="tab10", marker="o", ax=ax)
    ax.set_title("Monthly Sales Trend by Year")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    ax.set_xticks(range(1, 13), MONTH_LABELS)
    ax.yaxis.set_major_formatter(DOLLARS)
    fig.tight_layout()
    fig.savefig(VISUALS_DIR / "monthly_sales.png", dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def top_products(df: pd.DataFrame, n: int = 5) -> pd.Series:
    return df.groupby("Product Name")["Sales"].sum().nlargest(n)


def plot_top_products(df: pd.DataFrame, show: bool) -> None:
    top = top_products(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    top.plot(kind="barh", color="steelblue", ax=ax)
    ax.invert_yaxis()  # biggest seller at the top
    ax.set_title("Top 5 Products by Sales", pad=20)
    ax.set_xlabel("Sales", labelpad=10)
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(DOLLARS)
    fig.savefig(VISUALS_DIR / "top_products.png", bbox_inches="tight", dpi=300)
    if show:
        plt.show()
    plt.close(fig)


def plot_top_products_interactive(df: pd.DataFrame, show: bool) -> None:
    top = top_products(df).reset_index()

    fig = px.bar(top, x="Sales", y="Product Name",
                 title="Top 5 Products by Sales (Interactive)",
                 color="Sales", color_continuous_scale="reds")
    fig.update_layout(xaxis_title="Sales ($)", yaxis_title="Product",
                      yaxis={"categoryorder": "total ascending"},
                      hovermode="y unified")
    fig.write_html(VISUALS_DIR / "top_products_interactive.html")
    if show:
        fig.show()


def main() -> None:
    show = "--no-show" not in sys.argv
    VISUALS_DIR.mkdir(exist_ok=True)

    df = load_data(DATA_PATH)
    print(df.head())
    print("\nMissing values:\n", df.isnull().sum())

    plot_sales_by_category(df, show)
    plot_monthly_sales(df, show)
    plot_top_products(df, show)
    plot_top_products_interactive(df, show)
    print(f"\nCharts saved to {VISUALS_DIR}")


if __name__ == "__main__":
    main()