import pytest

pytest.importorskip("duckdb")

from sales_analysis import metrics, sql  # noqa: E402


def test_every_query_runs(sample_csv):
    for name in sql.list_queries():
        assert not sql.run_query(name, sample_csv).empty, name


def test_unknown_query_raises():
    with pytest.raises(ValueError, match="Unknown query"):
        sql.read_query("does_not_exist")


def test_view_removes_the_duplicate(sample_csv):
    result = sql.run_query("sales_by_category", sample_csv)
    assert result["total_sales"].sum() == pytest.approx(2750)


def test_category_totals_match_pandas(sample, sample_csv):
    from_sql = sql.run_query("sales_by_category", sample_csv).set_index("category")
    from_pandas = metrics.sales_by_category(sample)
    for category, value in from_pandas.items():
        assert from_sql.loc[category, "total_sales"] == pytest.approx(value)


def test_yearly_growth_matches_pandas(sample_csv):
    result = sql.run_query("yearly_growth", sample_csv).set_index("year")
    assert result.loc[2018, "growth_pct"] == pytest.approx(50)


def test_shipping_times_match_pandas(sample, sample_csv):
    from_sql = sql.run_query("shipping_times", sample_csv).set_index("ship_mode")
    from_pandas = metrics.shipping_times(sample)
    for mode in from_sql.index:
        assert from_sql.loc[mode, "orders"] == from_pandas.loc[mode, "Orders"]
        assert from_sql.loc[mode, "avg_days"] == pytest.approx(from_pandas.loc[mode, "Average"])


def test_top_customer_matches_pandas(sample, sample_csv):
    from_sql = sql.run_query("top_customers", sample_csv)
    from_pandas = metrics.top_customers(sample, 1)
    assert from_sql["customer_id"].iloc[0] == from_pandas["Customer ID"].iloc[0]
