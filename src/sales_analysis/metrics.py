"""Aggregations used by the charts. No plotting happens here."""

import pandas as pd

STATE_CODES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

SHIP_MODE_ORDER = ["Same Day", "First Class", "Second Class", "Standard Class"]


# ---------------------------------------------------------------- overview


def sales_by_category(df: pd.DataFrame) -> pd.Series:
    """Total sales per category, largest first."""
    return df.groupby("Category")["Sales"].sum().sort_values(ascending=False)


def summary(df: pd.DataFrame) -> dict:
    """Headline numbers for the whole dataset."""
    orders = df["Order ID"].nunique()
    return {
        "total_sales": float(df["Sales"].sum()),
        "orders": orders,
        "customers": df["Customer ID"].nunique(),
        "avg_order_value": float(df["Sales"].sum() / orders),
        "first_order": df["Order Date"].min().date(),
        "last_order": df["Order Date"].max().date(),
    }


# ---------------------------------------------------------------- time


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales for every year and month, with columns Year, Month, Sales."""
    return df.groupby(["Year", "Month"])["Sales"].sum().reset_index()


def yearly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Sales per year plus growth on the previous year in percent."""
    yearly = df.groupby("Year")["Sales"].sum().reset_index()
    yearly["Growth %"] = yearly["Sales"].pct_change() * 100
    return yearly


def seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Sales as a Year x Month grid (rows are years, columns are months 1 to 12)."""
    return df.pivot_table(
        index="Year", columns="Month", values="Sales", aggfunc="sum", fill_value=0
    ).reindex(columns=range(1, 13), fill_value=0)


def month_index(df: pd.DataFrame) -> pd.Series:
    """Each calendar month's sales relative to the average month (1.0 = average)."""
    by_month = df.groupby("Month")["Sales"].sum()
    return by_month / by_month.mean()


# ---------------------------------------------------------------- geography


def sales_by_region(df: pd.DataFrame) -> pd.Series:
    """Total sales per region, largest first."""
    return df.groupby("Region")["Sales"].sum().sort_values(ascending=False)


def sales_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and order count per state, with the two letter state code."""
    states = (
        df.groupby("State")
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    states["Code"] = states["State"].map(STATE_CODES)
    return states.sort_values("Sales", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------- customers


def sales_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Sales, customers and sales per customer for each segment."""
    seg = df.groupby("Segment").agg(Sales=("Sales", "sum"), Customers=("Customer ID", "nunique"))
    seg["Sales per Customer"] = seg["Sales"] / seg["Customers"]
    return seg.sort_values("Sales", ascending=False)


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """The ``n`` customers with the highest total sales."""
    return (
        df.groupby(["Customer ID", "Customer Name"])
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .nlargest(n, "Sales")
        .reset_index()
    )


def _score(values: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Score values 1 to 4 by quartile. Ranking first avoids ties breaking qcut."""
    ranks = values.rank(method="first", ascending=higher_is_better)
    return pd.qcut(ranks, 4, labels=[1, 2, 3, 4]).astype(int)


RFM_SEGMENTS = ["Champions", "Loyal", "Needs Attention", "At Risk", "Lost"]


def _rfm_segment(r: int, f: int, m: int) -> str:
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    if f >= 3:
        return "Loyal" if r >= 2 else "At Risk"
    if r >= 3:
        return "Needs Attention"
    if r == 2:
        return "At Risk"
    return "Lost"


def rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Recency, frequency and monetary scores per customer, plus a segment.

    Recency is days since the customer's last order, measured from the day
    after the last order in the data. Each measure is scored 1 (worst) to 4
    (best) by quartile.
    """
    snapshot = df["Order Date"].max() + pd.Timedelta(days=1)
    table = df.groupby("Customer ID").agg(
        Recency=("Order Date", lambda d: (snapshot - d.max()).days),
        Frequency=("Order ID", "nunique"),
        Monetary=("Sales", "sum"),
    )
    table["R"] = _score(table["Recency"], higher_is_better=False)
    table["F"] = _score(table["Frequency"])
    table["M"] = _score(table["Monetary"])
    table["Segment"] = [
        _rfm_segment(r, f, m) for r, f, m in zip(table["R"], table["F"], table["M"], strict=True)
    ]
    return table


def rfm_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Customers and sales per RFM segment, in a fixed best to worst order."""
    table = rfm(df)
    out = table.groupby("Segment").agg(Customers=("Monetary", "size"), Sales=("Monetary", "sum"))
    out["Share of Sales %"] = out["Sales"] / out["Sales"].sum() * 100
    return out.reindex(RFM_SEGMENTS).fillna(0)


# ---------------------------------------------------------------- shipping


def shipping_times(df: pd.DataFrame) -> pd.DataFrame:
    """Average, median and max days from order to shipping per ship mode."""
    orders = df.drop_duplicates("Order ID")  # one row per order, not per line
    return (
        orders.groupby("Ship Mode")["Ship Days"]
        .agg(Orders="size", Average="mean", Median="median", Max="max")
        .reindex(SHIP_MODE_ORDER)
    )


# ---------------------------------------------------------------- products


def top_products(df: pd.DataFrame, n: int = 5) -> pd.Series:
    """The ``n`` products with the highest total sales, largest first."""
    return df.groupby("Product Name")["Sales"].sum().nlargest(n)


def subcategory_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Sales per sub-category with its parent category, largest first."""
    return (
        df.groupby(["Category", "Sub-Category"])["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
        .reset_index(drop=True)
    )


def pareto(df: pd.DataFrame) -> pd.DataFrame:
    """Products ranked by sales with cumulative share of products and of sales."""
    by_product = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
    out = by_product.reset_index()
    out["Product Share %"] = (out.index + 1) / len(out) * 100
    out["Sales Share %"] = out["Sales"].cumsum() / out["Sales"].sum() * 100
    return out


def products_for_share(df: pd.DataFrame, share: float = 80.0) -> float:
    """Percent of products needed to reach ``share`` percent of total sales."""
    table = pareto(df)
    reached = table[table["Sales Share %"] >= share].iloc[0]
    return float(reached["Product Share %"])


# ---------------------------------------------------------------- insights


def insights(df: pd.DataFrame) -> dict:
    """Key findings, computed from the data so the README never goes stale."""
    yearly = yearly_sales(df)
    index = month_index(df)
    region = sales_by_region(df)
    category = sales_by_category(df)
    segments = sales_by_segment(df)
    ship = shipping_times(df)
    rfm_table = rfm_summary(df)
    return {
        "top_category": category.index[0],
        "top_category_share": float(category.iloc[0] / category.sum() * 100),
        "best_month": int(index.idxmax()),
        "best_month_vs_avg": float((index.max() - 1) * 100),
        "latest_year": int(yearly["Year"].iloc[-1]),
        "latest_growth": float(yearly["Growth %"].iloc[-1]),
        "top_region": region.index[0],
        "top_region_share": float(region.iloc[0] / region.sum() * 100),
        "top_segment": segments.index[0],
        "top_segment_share": float(segments["Sales"].iloc[0] / segments["Sales"].sum() * 100),
        "products_for_80pct": products_for_share(df, 80),
        "standard_ship_days": float(ship.loc["Standard Class", "Average"]),
        "champions_share": float(rfm_table.loc["Champions", "Share of Sales %"]),
    }
