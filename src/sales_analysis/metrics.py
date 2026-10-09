"""Aggregations used by the charts. No plotting happens here."""

import pandas as pd


def sales_by_category(df: pd.DataFrame) -> pd.Series:
    """Total sales per category, largest first."""
    return df.groupby("Category")["Sales"].sum().sort_values(ascending=False)


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales for every year and month, with columns Year, Month, Sales."""
    return df.groupby(["Year", "Month"])["Sales"].sum().reset_index()


def top_products(df: pd.DataFrame, n: int = 5) -> pd.Series:
    """The ``n`` products with the highest total sales, largest first."""
    return df.groupby("Product Name")["Sales"].sum().nlargest(n)


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
