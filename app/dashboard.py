"""Interactive sales dashboard.

Run from the repo root:
    streamlit run app/dashboard.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from sales_analysis import forecast, metrics
from sales_analysis.data import load_data
from sales_analysis.filters import filter_sales, previous_period
from sales_analysis.plots import BLUES, MONTH_LABELS, PALETTE

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "train.csv"
ACCENT = PALETTE[0]
MONEY = "$%{x:,.0f}"

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data(DATA_PATH)


@st.cache_data(show_spinner="Fitting forecast models...")
def get_forecast(regions: tuple, categories: tuple, segments: tuple, months: int):
    """Cached so moving other widgets doesn't refit the models."""
    subset = filter_sales(
        get_data(), regions=list(regions), categories=list(categories), segments=list(segments)
    )
    return forecast.run_forecast(subset, horizon=months)


def style(fig, height: int = 380):
    """Apply the same clean look to every Plotly chart."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        title={"x": 0, "font": {"size": 16}},
        hoverlabel={"bgcolor": "white"},
    )
    return fig


def money(value: float) -> str:
    return f"${value:,.0f}"


def change(current: float, previous: float) -> str | None:
    if not previous:
        return None
    return f"{(current - previous) / previous * 100:+.1f}% vs previous period"


# ------------------------------------------------------------------ sidebar

df_all = get_data()
first_day = df_all["Order Date"].min().date()
last_day = df_all["Order Date"].max().date()

st.sidebar.header("Filters")
picked = st.sidebar.date_input(
    "Order date",
    value=(first_day, last_day),
    min_value=first_day,
    max_value=last_day,
)
if not isinstance(picked, tuple) or len(picked) != 2:
    st.info("Pick an end date to apply the date filter.")
    st.stop()
start, end = picked


def multiselect(label: str, column: str) -> list[str]:
    options = sorted(df_all[column].unique())
    return st.sidebar.multiselect(label, options, default=options)


regions = multiselect("Region", "Region")
categories = multiselect("Category", "Category")
segments = multiselect("Segment", "Segment")

filters = {"regions": regions, "categories": categories, "segments": segments}
df = filter_sales(df_all, start, end, **filters)

st.sidebar.download_button(
    "Download filtered data (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales.csv",
    mime="text/csv",
    disabled=df.empty,
)

# ------------------------------------------------------------------ header

st.title("📊 Sales Performance Dashboard")
st.caption(f"Superstore orders from {start:%d %b %Y} to {end:%d %b %Y}")

if df.empty:
    st.warning("No orders match these filters. Try widening them in the sidebar.")
    st.stop()

# ------------------------------------------------------------------ KPI tiles

now = metrics.summary(df)
prev_start, prev_end = previous_period(start, end)
df_prev = filter_sales(df_all, prev_start, prev_end, **filters)
before = metrics.summary(df_prev) if not df_prev.empty else None


def delta(key: str) -> str | None:
    return change(now[key], before[key]) if before else None


k1, k2, k3, k4 = st.columns(4)
k1.metric("Total sales", money(now["total_sales"]), delta("total_sales"), border=True)
k2.metric("Orders", f"{now['orders']:,}", delta("orders"), border=True)
k3.metric("Customers", f"{now['customers']:,}", delta("customers"), border=True)
k4.metric("Avg order value", money(now["avg_order_value"]), delta("avg_order_value"), border=True)
if before is None:
    st.caption("No earlier period of the same length in the data, so no comparison is shown.")

# ------------------------------------------------------------------ tabs

overview, products, customers, geography, shipping, outlook = st.tabs(
    ["Overview", "Products", "Customers", "Geography", "Shipping", "Forecast"]
)

with overview:
    trend = df.set_index("Order Date")["Sales"].resample("MS").sum().reset_index()
    fig = px.line(
        trend,
        x="Order Date",
        y="Sales",
        markers=True,
        title="Monthly sales",
        color_discrete_sequence=[ACCENT],
    )
    fig.update_traces(hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>")
    fig.update_layout(xaxis_title="", yaxis_title="Sales ($)")
    st.plotly_chart(style(fig), width="stretch")

    left, right = st.columns(2)
    by_cat = metrics.sales_by_category(df).reset_index()
    fig = px.bar(
        by_cat, x="Category", y="Sales", title="Sales by category", color_discrete_sequence=[ACCENT]
    )
    fig.update_traces(hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>")
    fig.update_layout(xaxis_title="", yaxis_title="Sales ($)")
    left.plotly_chart(style(fig), width="stretch")

    grid = metrics.seasonality(df)
    fig = px.imshow(
        grid / 1000,
        x=MONTH_LABELS,
        y=grid.index.astype(str),
        color_continuous_scale=BLUES,
        text_auto=".0f",
        aspect="auto",
        title="Seasonality ($k by month and year)",
    )
    fig.update_traces(hovertemplate="%{x} %{y}<br>$%{z:,.1f}k<extra></extra>")
    fig.update_layout(coloraxis_colorbar={"title": "$k"})
    right.plotly_chart(style(fig), width="stretch")

with products:
    n = st.slider("How many top products?", 5, 20, 10)
    top = metrics.top_products(df, n).reset_index()
    fig = px.bar(
        top,
        x="Sales",
        y="Product Name",
        orientation="h",
        title=f"Top {n} products by sales",
        color_discrete_sequence=[ACCENT],
    )
    fig.update_traces(hovertemplate="%{y}<br>" + MONEY + "<extra></extra>")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending", "title": ""}, xaxis_title="Sales ($)"
    )
    st.plotly_chart(style(fig, height=120 + 32 * n), width="stretch")

    left, right = st.columns(2)
    sub = metrics.subcategory_sales(df)
    fig = px.bar(
        sub,
        x="Sales",
        y="Sub-Category",
        color="Category",
        orientation="h",
        title="Sales by sub-category",
        color_discrete_sequence=PALETTE,
        category_orders={"Category": sorted(df_all["Category"].unique())},
    )
    fig.update_traces(hovertemplate="%{y}<br>" + MONEY + "<extra></extra>")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis_title="Sales ($)",
        legend_title="",
    )
    left.plotly_chart(style(fig, height=520), width="stretch")

    pareto = metrics.pareto(df)
    share = metrics.products_for_share(df, 80)
    fig = px.line(
        pareto,
        x="Product Share %",
        y="Sales Share %",
        title=f"{share:.0f}% of products bring in 80% of sales",
        color_discrete_sequence=[ACCENT],
    )
    fig.add_hline(y=80, line_dash="dash", line_color="#b4b2ab")
    fig.add_vline(x=share, line_dash="dash", line_color="#b4b2ab")
    fig.update_traces(
        hovertemplate="Top %{x:.0f}% of products<br>%{y:.0f}% of sales<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="Share of products (%)", yaxis_title="Cumulative share of sales (%)"
    )
    right.plotly_chart(style(fig, height=520), width="stretch")

with customers:
    left, right = st.columns(2)
    seg = metrics.sales_by_segment(df).reset_index()
    fig = px.bar(
        seg,
        x="Segment",
        y="Sales",
        title="Sales by segment",
        color_discrete_sequence=[ACCENT],
        hover_data={"Customers": True, "Sales per Customer": ":$,.0f"},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Sales ($)")
    left.plotly_chart(style(fig), width="stretch")

    if df["Customer ID"].nunique() < 20:
        right.info("Widen the filters to see RFM segments. Scoring needs at least 20 customers.")
    else:
        rfm = metrics.rfm_summary(df).reset_index()
        fig = px.bar(
            rfm,
            x="Customers",
            y="Segment",
            orientation="h",
            title="Customer segments (RFM)",
            color_discrete_sequence=[ACCENT],
            hover_data={"Sales": ":$,.0f", "Share of Sales %": ":.1f"},
        )
        fig.update_layout(
            yaxis={
                "categoryorder": "array",
                "categoryarray": metrics.RFM_SEGMENTS[::-1],
                "title": "",
            }
        )
        right.plotly_chart(style(fig), width="stretch")

    with st.expander("What do the RFM segments mean?"):
        st.markdown(
            "Each customer gets a score from 1 to 4 for **Recency** (how recently "
            "they ordered), **Frequency** (how many orders) and **Monetary** "
            "(how much they spent).\n\n"
            "- **Champions**: recent, frequent and high spending\n"
            "- **Loyal**: order often and still fairly recent\n"
            "- **Needs Attention**: ordered recently but not often\n"
            "- **At Risk**: used to order, haven't for a while\n"
            "- **Lost**: no recent orders and low frequency"
        )

    st.markdown("**Top customers**")
    st.dataframe(
        metrics.top_customers(df, 10),
        hide_index=True,
        width="stretch",
        column_config={"Sales": st.column_config.NumberColumn(format="dollar")},
    )

with geography:
    states = metrics.sales_by_state(df)
    fig = px.choropleth(
        states,
        locations="Code",
        locationmode="USA-states",
        scope="usa",
        color="Sales",
        hover_name="State",
        color_continuous_scale=BLUES,
        title="Sales by state",
        hover_data={"Code": False, "Sales": ":$,.0f", "Orders": ":,"},
    )
    fig.update_layout(coloraxis_colorbar={"title": "Sales ($)"})
    st.plotly_chart(style(fig, height=480), width="stretch")

    left, right = st.columns(2)
    region = metrics.sales_by_region(df).reset_index()
    fig = px.bar(
        region,
        x="Sales",
        y="Region",
        orientation="h",
        title="Sales by region",
        color_discrete_sequence=[ACCENT],
    )
    fig.update_traces(hovertemplate="%{y}<br>" + MONEY + "<extra></extra>")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending", "title": ""}, xaxis_title="Sales ($)"
    )
    left.plotly_chart(style(fig), width="stretch")

    right.markdown("**Top 10 states**")
    right.dataframe(
        states.head(10)[["State", "Sales", "Orders"]],
        hide_index=True,
        width="stretch",
        column_config={"Sales": st.column_config.NumberColumn(format="dollar")},
    )

with shipping:
    orders = df.drop_duplicates("Order ID")
    fig = px.box(
        orders,
        x="Ship Days",
        y="Ship Mode",
        orientation="h",
        title="Days from order to shipping",
        category_orders={"Ship Mode": metrics.SHIP_MODE_ORDER},
        color_discrete_sequence=[ACCENT],
    )
    fig.update_layout(xaxis_title="Days", yaxis_title="")
    st.plotly_chart(style(fig), width="stretch")

    st.dataframe(
        metrics.shipping_times(df).reset_index(),
        hide_index=True,
        width="stretch",
        column_config={
            "Average": st.column_config.NumberColumn(format="%.1f days"),
            "Median": st.column_config.NumberColumn(format="%.0f days"),
            "Max": st.column_config.NumberColumn(format="%d days"),
        },
    )

with outlook:
    st.caption(
        "The forecast uses all dates in the data, so the date filter does not "
        "apply here. Region, category and segment filters do."
    )
    months = st.slider("Months to forecast", 3, 12, 6)
    try:
        result = get_forecast(tuple(regions), tuple(categories), tuple(segments), months)
    except ValueError as err:
        st.info(f"Can't forecast this selection: {err} Try widening the filters.")
        st.stop()

    best = result.backtest.loc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Model used", result.model, border=True)
    c2.metric(
        "Backtest error (MAPE)",
        f"{best['MAPE %']:.1f}%",
        border=True,
        help="Average % miss per month when the model, trained on "
        "2015 to 2017, predicted 2018. Lower is better.",
    )
    c3.metric(
        f"Forecast, next {months} months", money(result.forecast["Forecast"].sum()), border=True
    )
    if best["MAPE %"] > 40:
        st.warning(
            "This selection's monthly sales swing a lot, so the forecast "
            "is rough. Treat it as a direction, not a number."
        )

    history = result.history.iloc[-24:].reset_index()
    history.columns = ["Month", "Sales"]
    fc = result.forecast
    last = history.iloc[-1]
    fig = px.line(
        history,
        x="Month",
        y="Sales",
        markers=True,
        title="Monthly sales and forecast",
        color_discrete_sequence=[ACCENT],
    )
    fig.data[0].name = "Actual"
    fig.data[0].showlegend = True
    fig.add_scatter(
        x=fc["Month"],
        y=fc["Upper"],
        mode="lines",
        line={"width": 0},
        showlegend=False,
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=fc["Month"],
        y=fc["Lower"],
        mode="lines",
        line={"width": 0},
        fill="tonexty",
        fillcolor="rgba(235, 104, 52, 0.15)",
        name="80% range",
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=[last["Month"], *fc["Month"]],
        y=[last["Sales"], *fc["Forecast"]],
        mode="lines+markers",
        name="Forecast",
        line={"color": PALETTE[1], "dash": "dash"},
    )
    fig.update_traces(
        hovertemplate="%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>", selector={"mode": "lines+markers"}
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Sales ($)",
        legend={"orientation": "h", "y": 1.08, "x": 1, "xanchor": "right"},
    )
    st.plotly_chart(style(fig, height=440), width="stretch")

    left, right = st.columns(2)
    left.markdown("**Forecast by month**")
    left.dataframe(
        fc.assign(Month=fc["Month"].dt.strftime("%b %Y")),
        hide_index=True,
        width="stretch",
        column_config={
            c: st.column_config.NumberColumn(format="dollar")
            for c in ["Forecast", "Lower", "Upper"]
        },
    )
    right.markdown("**How the models did on 2018**")
    right.dataframe(
        result.backtest,
        hide_index=True,
        width="stretch",
        column_config={
            "MAPE %": st.column_config.NumberColumn(format="%.1f%%"),
            "MAE $": st.column_config.NumberColumn(format="dollar"),
        },
    )
    with st.expander("How does the forecast work?"):
        st.markdown(
            "Two models are trained on 2015 to 2017 and asked to predict 2018, "
            "which we already know. The one that misses by less is used.\n\n"
            "- **Seasonal naive + growth**: next month looks like the same month "
            "last year, scaled by last year's growth. A simple baseline.\n"
            "- **Holt-Winters**: exponential smoothing that learns a trend and a "
            "repeating yearly pattern, giving more weight to recent months.\n\n"
            "The shaded range shows where 8 in 10 months would land if the model "
            "keeps missing by about as much as it did in 2018."
        )
