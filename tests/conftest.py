from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sales_analysis.data import load_data

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURES / "sample.csv"


@pytest.fixture(scope="session")
def sample_csv() -> Path:
    return SAMPLE_CSV


@pytest.fixture
def sample() -> pd.DataFrame:
    """The cleaned sample dataset. A fresh copy per test, so tests can't leak."""
    return load_data(SAMPLE_CSV)


@pytest.fixture(scope="session")
def seasonal_sales() -> pd.DataFrame:
    """Four years of synthetic monthly sales with a trend and a yearly pattern.

    One order on the first of each month, in the same shape as the real data,
    so it can go straight into the forecast functions.
    """
    months = pd.date_range("2015-01-01", periods=48, freq="MS")
    t = np.arange(48)
    sales = 1000 + 15 * t + 400 * np.sin(2 * np.pi * t / 12)
    return pd.DataFrame({"Order Date": months, "Sales": sales})
