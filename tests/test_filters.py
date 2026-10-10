from datetime import date

from sales_analysis.filters import filter_sales, previous_period


def test_no_filters_returns_everything(sample):
    assert len(filter_sales(sample)) == len(sample)


def test_region_filter(sample):
    result = filter_sales(sample, regions=["West"])
    assert set(result["Region"]) == {"West"}
    assert len(result) == 3


def test_date_range_is_inclusive(sample):
    result = filter_sales(sample, start=date(2017, 1, 5), end=date(2017, 1, 5))
    assert result["Order ID"].unique().tolist() == ["O-1"]


def test_filters_combine(sample):
    result = filter_sales(
        sample, start=date(2018, 1, 1), categories=["Technology"], segments=["Consumer"]
    )
    assert result["Order ID"].tolist() == ["O-6"]


def test_empty_selection_returns_no_rows(sample):
    assert filter_sales(sample, regions=[]).empty


def test_previous_period_has_the_same_length():
    assert previous_period(date(2018, 1, 1), date(2018, 1, 31)) == (
        date(2017, 12, 1),
        date(2017, 12, 31),
    )
