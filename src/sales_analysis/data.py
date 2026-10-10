"""Loading, validating and cleaning the raw sales data."""

from pathlib import Path

import pandas as pd

DATE_FORMAT = "%d/%m/%Y"

REQUIRED_COLUMNS = [
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Segment",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
]


def validate(df: pd.DataFrame) -> None:
    """Fail early with a clear message if the CSV is missing columns."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Data is missing required columns: {missing}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix types, remove duplicate order lines and add helper columns."""
    df = df.copy()

    # Dates are stored day first, e.g. 08/11/2017 is 8 November 2017
    df["Order Date"] = pd.to_datetime(df["Order Date"], format=DATE_FORMAT)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format=DATE_FORMAT)

    # Postal codes are read as floats because a few are missing. Store them
    # as 5 character strings so leading zeros survive (e.g. 05401).
    df["Postal Code"] = df["Postal Code"].astype("Int64").astype("string").str.zfill(5)

    # The same order line can appear twice with a different Row ID
    subset = [col for col in df.columns if col != "Row ID"]
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Quarter"] = df["Order Date"].dt.quarter
    df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df


def load_data(path: str | Path) -> pd.DataFrame:
    """Read the CSV at ``path`` and return a clean DataFrame."""
    df = pd.read_csv(path)
    validate(df)
    return clean(df)
