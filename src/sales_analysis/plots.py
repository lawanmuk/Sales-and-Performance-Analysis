"""Static (matplotlib) and interactive (plotly) charts.

Every function takes the clean DataFrame and an output folder, saves its
chart there and returns the path of the saved file.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import plotly.express as px
import seaborn as sns

from sales_analysis import metrics

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOLLARS = mticker.StrMethodFormatter("${x:,.0f}")


def _finish(fig, path: Path, show: bool, **save_kwargs) -> Path:
    fig.savefig(path, **save_kwargs)
    if show:
        plt.show()
    plt.close(fig)
    return path


def sales_by_category(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    sales = metrics.sales_by_category(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    sales.plot(kind="bar", color=["skyblue", "orange", "green"], ax=ax)
    ax.set_title("Total Sales by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Sales")
    ax.yaxis.set_major_formatter(DOLLARS)
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    return _finish(fig, out_dir / "sales_by_category.png", show, dpi=150)


def monthly_sales(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    monthly = metrics.monthly_sales(df)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly, x="Month", y="Sales", hue="Year",
                 palette="tab10", marker="o", ax=ax)
    ax.set_title("Monthly Sales Trend by Year")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    ax.set_xticks(range(1, 13), MONTH_LABELS)
    ax.yaxis.set_major_formatter(DOLLARS)
    fig.tight_layout()
    return _finish(fig, out_dir / "monthly_sales.png", show, dpi=150)


def top_products(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    top = metrics.top_products(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    top.plot(kind="barh", color="steelblue", ax=ax)
    ax.invert_yaxis()  # biggest seller at the top
    ax.set_title("Top 5 Products by Sales", pad=20)
    ax.set_xlabel("Sales", labelpad=10)
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(DOLLARS)
    return _finish(fig, out_dir / "top_products.png", show,
                   bbox_inches="tight", dpi=300)


def top_products_interactive(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    top = metrics.top_products(df).reset_index()

    fig = px.bar(top, x="Sales", y="Product Name",
                 title="Top 5 Products by Sales (Interactive)",
                 color="Sales", color_continuous_scale="reds")
    fig.update_layout(xaxis_title="Sales ($)", yaxis_title="Product",
                      yaxis={"categoryorder": "total ascending"},
                      hovermode="y unified")
    path = out_dir / "top_products_interactive.html"
    fig.write_html(path)
    if show:
        fig.show()
    return path


ALL_CHARTS = [sales_by_category, monthly_sales, top_products, top_products_interactive]
