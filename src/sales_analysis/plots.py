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

# One palette for every chart. Categorical colours are used in this fixed
# order (checked for colour blind separation); blues are for magnitude.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
ACCENT = PALETTE[0]
MUTED = "#b4b2ab"
BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
TEXT = "#52514e"

DOLLARS = mticker.StrMethodFormatter("${x:,.0f}")
DOLLARS_K = mticker.FuncFormatter(lambda x, _: f"${x / 1000:,.0f}k")

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": TEXT,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 14,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "grid.color": "#e4e3df",
    "legend.frameon": False,
})


def _finish(fig, path: Path, show: bool, **save_kwargs) -> Path:
    save_kwargs.setdefault("dpi", 150)
    save_kwargs.setdefault("bbox_inches", "tight")
    fig.savefig(path, **save_kwargs)
    if show:
        plt.show()
    plt.close(fig)
    return path


def _value_grid(ax, axis: str = "y") -> None:
    ax.grid(axis=axis)
    ax.set_axisbelow(True)


# ================================================================ overview

def sales_by_category(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    sales = metrics.sales_by_category(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(sales.index, sales.values, color=ACCENT, width=0.6)
    ax.set_title("Total Sales by Category")
    ax.set_xlabel("")
    ax.set_ylabel("Sales")
    ax.yaxis.set_major_formatter(DOLLARS_K)
    _value_grid(ax)
    return _finish(fig, out_dir / "sales_by_category.png", show)


# ================================================================ time

def monthly_sales(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    monthly = metrics.monthly_sales(df)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly, x="Month", y="Sales", hue="Year",
                 palette=PALETTE, marker="o", linewidth=2, markersize=7, ax=ax)
    ax.set_title("Monthly Sales Trend by Year")
    ax.set_xlabel("")
    ax.set_ylabel("Sales")
    ax.set_xticks(range(1, 13), MONTH_LABELS)
    ax.yaxis.set_major_formatter(DOLLARS_K)
    ax.legend(title="Year", loc="upper left")
    _value_grid(ax)
    return _finish(fig, out_dir / "monthly_sales.png", show)


def yearly_growth(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    yearly = metrics.yearly_sales(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(yearly["Year"].astype(str), yearly["Sales"], color=ACCENT, width=0.6)
    for bar, growth in zip(bars, yearly["Growth %"]):
        label = "" if pd.isna(growth) else f"{growth:+.1f}%"
        ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", color=TEXT, fontsize=11)
    ax.set_title("Yearly Sales and Growth on Previous Year")
    ax.set_ylabel("Sales")
    ax.yaxis.set_major_formatter(DOLLARS_K)
    ax.set_ylim(0, yearly["Sales"].max() * 1.12)
    _value_grid(ax)
    return _finish(fig, out_dir / "yearly_growth.png", show)


def seasonality_heatmap(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    grid = metrics.seasonality(df) / 1000

    fig, ax = plt.subplots(figsize=(12, 4.5))
    sns.heatmap(grid, cmap=sns.blend_palette(BLUES, as_cmap=True),
                annot=True, fmt=".0f", linewidths=2, linecolor="white",
                cbar_kws={"label": "Sales ($k)"}, ax=ax)
    ax.set_title("Seasonality: Sales by Month and Year ($k)")
    ax.set_xticks([i + 0.5 for i in range(12)], MONTH_LABELS, rotation=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="y", rotation=0)
    return _finish(fig, out_dir / "seasonality_heatmap.png", show)


# ================================================================ geography

def sales_by_region(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    region = metrics.sales_by_region(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(region.index, region.values, color=ACCENT, height=0.6)
    ax.invert_yaxis()
    share = region / region.sum() * 100
    for i, (value, pct) in enumerate(zip(region.values, share)):
        ax.text(value, i, f"  {pct:.0f}%", va="center", color=TEXT)
    ax.set_title("Sales by Region")
    ax.set_xlabel("Sales")
    ax.xaxis.set_major_formatter(DOLLARS_K)
    _value_grid(ax, "x")
    return _finish(fig, out_dir / "sales_by_region.png", show)


def state_map(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    states = metrics.sales_by_state(df)

    fig = px.choropleth(
        states, locations="Code", locationmode="USA-states", scope="usa",
        color="Sales", color_continuous_scale=BLUES,
        hover_name="State",
        hover_data={"Code": False, "Sales": ":$,.0f", "Orders": ":,"},
        title="Sales by State",
    )
    fig.update_layout(coloraxis_colorbar={"title": "Sales ($)"},
                      margin={"l": 0, "r": 0, "t": 50, "b": 0})
    path = out_dir / "sales_by_state_map.html"
    fig.write_html(path, include_plotlyjs="cdn")
    if show:
        fig.show()
    return path


# ================================================================ customers

def sales_by_segment(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    seg = metrics.sales_by_segment(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(seg.index, seg["Sales"], color=ACCENT, width=0.6)
    for bar, customers in zip(bars, seg["Customers"]):
        ax.annotate(f"{customers} customers",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", color=TEXT)
    ax.set_title("Sales by Customer Segment")
    ax.set_ylabel("Sales")
    ax.yaxis.set_major_formatter(DOLLARS_K)
    ax.set_ylim(0, seg["Sales"].max() * 1.12)
    _value_grid(ax)
    return _finish(fig, out_dir / "sales_by_segment.png", show)


def rfm_segments(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    table = metrics.rfm_summary(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(table.index, table["Customers"], color=ACCENT, height=0.6)
    ax.invert_yaxis()
    for i, (n, pct) in enumerate(zip(table["Customers"], table["Share of Sales %"])):
        ax.text(n, i, f"  {pct:.0f}% of sales", va="center", color=TEXT)
    ax.set_title("Customer Segments (RFM)")
    ax.set_xlabel("Customers")
    ax.set_xlim(0, table["Customers"].max() * 1.25)
    _value_grid(ax, "x")
    return _finish(fig, out_dir / "rfm_segments.png", show)


# ================================================================ shipping

def shipping_times(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    orders = df.drop_duplicates("Order ID")

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=orders, x="Ship Days", y="Ship Mode",
                order=metrics.SHIP_MODE_ORDER, color="#9ec5f4",
                linecolor=ACCENT, width=0.55, ax=ax)
    ax.set_title("Days from Order to Shipping by Ship Mode")
    ax.set_xlabel("Days")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    _value_grid(ax, "x")
    return _finish(fig, out_dir / "shipping_times.png", show)


# ================================================================ products

def top_products(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    top = metrics.top_products(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top.index, top.values, color=ACCENT, height=0.6)
    ax.invert_yaxis()  # biggest seller at the top
    ax.set_title("Top 5 Products by Sales")
    ax.set_xlabel("Sales")
    ax.xaxis.set_major_formatter(DOLLARS_K)
    _value_grid(ax, "x")
    return _finish(fig, out_dir / "top_products.png", show, dpi=300)


def top_products_interactive(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    top = metrics.top_products(df).reset_index()

    fig = px.bar(top, x="Sales", y="Product Name",
                 title="Top 5 Products by Sales (Interactive)",
                 color_discrete_sequence=[ACCENT])
    fig.update_traces(hovertemplate="%{y}<br>$%{x:,.0f}<extra></extra>")
    fig.update_layout(xaxis_title="Sales ($)", yaxis_title="",
                      yaxis={"categoryorder": "total ascending"},
                      plot_bgcolor="white")
    path = out_dir / "top_products_interactive.html"
    fig.write_html(path, include_plotlyjs="cdn")
    if show:
        fig.show()
    return path


def subcategory_sales(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    sub = metrics.subcategory_sales(df)
    categories = sorted(sub["Category"].unique())
    colours = dict(zip(categories, PALETTE))

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(sub["Sub-Category"], sub["Sales"],
            color=sub["Category"].map(colours), height=0.7)
    ax.invert_yaxis()
    handles = [plt.Rectangle((0, 0), 1, 1, color=colours[c]) for c in categories]
    ax.legend(handles, categories, loc="lower right")
    ax.set_title("Sales by Sub-Category")
    ax.set_xlabel("Sales")
    ax.xaxis.set_major_formatter(DOLLARS_K)
    _value_grid(ax, "x")
    return _finish(fig, out_dir / "subcategory_sales.png", show)


def pareto_curve(df: pd.DataFrame, out_dir: Path, show: bool = False) -> Path:
    table = metrics.pareto(df)
    share = metrics.products_for_share(df, 80)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(table["Product Share %"], table["Sales Share %"], color=ACCENT, linewidth=2)
    ax.axhline(80, color=MUTED, linestyle="--", linewidth=1)
    ax.axvline(share, color=MUTED, linestyle="--", linewidth=1)
    ax.annotate(f"{share:.0f}% of products bring in 80% of sales",
                (share, 80), xytext=(12, -28), textcoords="offset points", color=TEXT)
    ax.set_title("Pareto: Share of Sales from Top Products")
    ax.set_xlabel("Share of products (ranked by sales)")
    ax.set_ylabel("Cumulative share of sales")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 101)
    _value_grid(ax, "both")
    return _finish(fig, out_dir / "pareto_curve.png", show)


ALL_CHARTS = [
    sales_by_category,
    monthly_sales, yearly_growth, seasonality_heatmap,
    sales_by_region, state_map,
    sales_by_segment, rfm_segments,
    shipping_times,
    top_products, top_products_interactive, subcategory_sales, pareto_curve,
]
