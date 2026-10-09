"""Filtering helpers shared by the dashboard (and easy to unit test)."""

from datetime import date, timedelta

import pandas as pd


def filter_sales(
    df: pd.DataFrame,
    start: date | None = None,
    end: date | None = None,
    regions: list[str] | None = None,
    categories: list[str] | None = None,
    segments: list[str] | None = None,
) -> pd.DataFrame:
    """Return the rows matching every filter. ``None`` means no filter.

    ``start`` and ``end`` are inclusive calendar dates.
    """
    mask = pd.Series(True, index=df.index)
    order_day = df["Order Date"].dt.normalize()
    if start is not None:
        mask &= order_day >= pd.Timestamp(start)
    if end is not None:
        mask &= order_day <= pd.Timestamp(end)
    if regions is not None:
        mask &= df["Region"].isin(regions)
    if categories is not None:
        mask &= df["Category"].isin(categories)
    if segments is not None:
        mask &= df["Segment"].isin(segments)
    return df[mask]


def previous_period(start: date, end: date) -> tuple[date, date]:
    """The period of the same length that ends the day before ``start``."""
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    return prev_end - timedelta(days=length - 1), prev_end
