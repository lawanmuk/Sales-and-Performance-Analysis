import pytest

from sales_analysis import metrics


def test_sales_by_category(sample):
    result = metrics.sales_by_category(sample)
    assert result.to_dict() == pytest.approx(
        {"Technology": 1700, "Furniture": 900, "Office Supplies": 150}
    )
    assert result.index[0] == "Technology"  # largest first


def test_summary(sample):
    s = metrics.summary(sample)
    assert s["total_sales"] == pytest.approx(2750)
    assert s["orders"] == 6
    assert s["customers"] == 4
    assert s["avg_order_value"] == pytest.approx(2750 / 6)


def test_yearly_growth(sample):
    yearly = metrics.yearly_sales(sample).set_index("Year")
    assert yearly.loc[2017, "Sales"] == pytest.approx(1100)
    assert yearly.loc[2018, "Sales"] == pytest.approx(1650)
    assert yearly.loc[2018, "Growth %"] == pytest.approx(50)


def test_seasonality_grid_has_every_month(sample):
    grid = metrics.seasonality(sample)
    assert list(grid.columns) == list(range(1, 13))
    assert grid.loc[2018, 11] == pytest.approx(600)
    assert grid.loc[2018, 1] == 0  # empty months are 0, not missing


def test_month_index_averages_to_one(sample):
    assert metrics.month_index(sample).mean() == pytest.approx(1)


def test_sales_by_region(sample):
    result = metrics.sales_by_region(sample)
    assert result.to_dict() == pytest.approx(
        {"South": 950, "West": 900, "Central": 600, "East": 300}
    )


def test_sales_by_state_has_codes_for_every_state(sample):
    states = metrics.sales_by_state(sample)
    assert states["Code"].notna().all()
    assert states.loc[states["State"] == "Vermont", "Orders"].item() == 2


def test_top_products(sample):
    top = metrics.top_products(sample, 2)
    assert top.index.tolist() == ["Phone A", "Chair A, Black"]
    assert top.iloc[0] == pytest.approx(1700)


def test_top_customers(sample):
    top = metrics.top_customers(sample, 1).iloc[0]
    assert top["Customer Name"] == "Dan Fox"
    assert top["Orders"] == 1


def test_shipping_times_count_each_order_once(sample):
    ship = metrics.shipping_times(sample)
    assert ship.loc["First Class", "Orders"] == 2  # O-1 has two lines but is one order
    assert ship.loc["First Class", "Average"] == pytest.approx(2)
    assert ship.loc["Standard Class", "Average"] == pytest.approx(5)
    assert ship.loc["Same Day", "Max"] == 0


def test_pareto_is_cumulative_and_ends_at_100(sample):
    table = metrics.pareto(sample)
    assert table["Sales Share %"].is_monotonic_increasing
    assert table["Sales Share %"].iloc[-1] == pytest.approx(100)
    assert table["Product Share %"].iloc[-1] == pytest.approx(100)


def test_products_for_share(sample):
    # Phone A alone is 62% of sales, adding Chair A reaches 95%: 2 of 4 products
    assert metrics.products_for_share(sample, 80) == pytest.approx(50)


def test_rfm_scores_and_segments_are_valid(sample):
    table = metrics.rfm(sample)
    assert len(table) == 4
    for col in ["R", "F", "M"]:
        assert table[col].between(1, 4).all()
    assert set(table["Segment"]) <= set(metrics.RFM_SEGMENTS)


def test_rfm_summary_accounts_for_every_customer_and_dollar(sample):
    summary = metrics.rfm_summary(sample)
    assert summary["Customers"].sum() == 4
    assert summary["Sales"].sum() == pytest.approx(2750)
    assert summary["Share of Sales %"].sum() == pytest.approx(100)


@pytest.mark.parametrize(
    ("r", "f", "m", "expected"),
    [
        (4, 4, 4, "Champions"),
        (2, 4, 1, "Loyal"),
        (1, 4, 4, "At Risk"),
        (4, 1, 1, "Needs Attention"),
        (2, 1, 1, "At Risk"),
        (1, 1, 1, "Lost"),
    ],
)
def test_rfm_segment_rules(r, f, m, expected):
    assert metrics._rfm_segment(r, f, m) == expected


def test_insights_match_the_sample(sample):
    i = metrics.insights(sample)
    assert i["top_category"] == "Technology"
    assert i["top_region"] == "South"
    assert i["best_month"] == 12  # Dec: 950 beats Nov: 250 + 600
    assert i["latest_year"] == 2018
    assert i["latest_growth"] == pytest.approx(50)
