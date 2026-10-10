import pandas as pd
import pytest

from sales_analysis import forecast


def test_monthly_series_fills_empty_months(sample):
    series = forecast.monthly_series(sample)
    assert len(series) == 24  # Jan 2017 to Dec 2018
    assert series[pd.Timestamp("2017-04-01")] == 0


def test_mape_and_mae():
    actual = pd.Series([100.0, 200.0])
    predicted = pd.Series([110.0, 180.0])
    assert forecast.mape(actual, predicted) == pytest.approx(10)
    assert forecast.mae(actual, predicted) == pytest.approx(15)


def test_seasonal_naive_repeats_last_year_scaled_by_growth(seasonal_sales):
    series = forecast.monthly_series(seasonal_sales)
    result = forecast.seasonal_naive(series, 3)
    growth = series.iloc[-12:].sum() / series.iloc[-24:-12].sum()
    assert result.iloc[0] == pytest.approx(series.iloc[-12] * growth)
    assert result.index[0] == pd.Timestamp("2019-01-01")


def test_run_forecast_shape_and_band(seasonal_sales):
    result = forecast.run_forecast(seasonal_sales, horizon=6)
    fc = result.forecast
    assert len(fc) == 6
    assert fc["Month"].iloc[0] == pd.Timestamp("2019-01-01")
    assert (fc["Lower"] <= fc["Forecast"]).all()
    assert (fc["Forecast"] <= fc["Upper"]).all()
    assert (fc["Lower"] >= 0).all()
    assert set(result.backtest["Model"]) == set(forecast.MODELS)


def test_holt_winters_wins_on_a_clean_seasonal_trend(seasonal_sales):
    result = forecast.run_forecast(seasonal_sales)
    assert result.model == "Holt-Winters"
    assert result.backtest.loc[0, "MAPE %"] < 5


def test_too_little_history_raises(sample):
    with pytest.raises(ValueError, match="at least 36 months"):
        forecast.run_forecast(sample)


def test_sparse_history_raises(seasonal_sales):
    sparse = seasonal_sales.iloc[::2]  # every other month is empty
    with pytest.raises(ValueError, match="too sparse"):
        forecast.run_forecast(sparse)
