import pandas as pd
import pytest

from sales_analysis.data import load_data, validate


def test_removes_duplicate_order_line(sample):
    assert len(sample) == 7
    assert sample["Sales"].sum() == pytest.approx(2750)


def test_dates_are_parsed_day_first(sample):
    first = sample.loc[sample["Order ID"] == "O-1", "Order Date"].iloc[0]
    assert first == pd.Timestamp("2017-01-05")  # 05/01/2017 is 5 January, not 1 May


def test_adds_helper_columns(sample):
    row = sample.loc[sample["Order ID"] == "O-5"].iloc[0]
    assert (row["Year"], row["Month"], row["Quarter"]) == (2018, 11, 4)
    assert row["Ship Days"] == 5


def test_postal_codes_keep_leading_zero_and_missing_stays_missing(sample):
    vermont = sample.loc[sample["State"] == "Vermont", "Postal Code"]
    assert vermont.dropna().tolist() == ["05401"]
    assert vermont.isna().sum() == 1


def test_missing_columns_raise_a_clear_error():
    with pytest.raises(ValueError, match="Sales"):
        validate(pd.DataFrame({"Order ID": ["O-1"]}))


def test_load_data_rejects_a_csv_without_required_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("Order ID,Total\nO-1,10\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_data(bad)
