"""Monthly sales forecasting.

Two models are compared on a holdout year:

* Seasonal naive with growth: next year's month = same month last year,
  scaled by the growth of the last 12 months. A simple baseline that any
  real model has to beat.
* Holt-Winters exponential smoothing with a damped trend and additive
  yearly seasonality (statsmodels).

The model with the lower error on the holdout is refit on all the data and
used for the forecast. The prediction band comes from the holdout errors.
"""

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SEASON = 12
Z_80 = 1.2816  # 80% two sided band under a normal error
MAX_EMPTY_SHARE = 0.10  # refuse to forecast if more than 10% of months are empty


def monthly_series(df: pd.DataFrame) -> pd.Series:
    """Total sales per calendar month, with empty months filled as 0."""
    return df.set_index("Order Date")["Sales"].resample("MS").sum()


def _future_index(series: pd.Series, horizon: int) -> pd.DatetimeIndex:
    start = series.index[-1] + pd.offsets.MonthBegin(1)
    return pd.date_range(start, periods=horizon, freq="MS")


def seasonal_naive(train: pd.Series, horizon: int) -> pd.Series:
    """Same month last year, times the growth of the last 12 months."""
    growth = train.iloc[-SEASON:].sum() / train.iloc[-2 * SEASON : -SEASON].sum()
    last_year = train.iloc[-SEASON:].to_numpy()
    values = np.resize(last_year, horizon) * growth
    return pd.Series(values, index=_future_index(train, horizon))


def holt_winters(train: pd.Series, horizon: int) -> pd.Series:
    """Holt-Winters with damped additive trend and additive seasonality."""
    model = ExponentialSmoothing(
        train.to_numpy(),
        trend="add",
        damped_trend=True,
        seasonal="add",
        seasonal_periods=SEASON,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # convergence chatter on small data
        fitted = model.fit()
    values = np.clip(fitted.forecast(horizon), 0, None)  # sales can't go negative
    return pd.Series(values, index=_future_index(train, horizon))


MODELS = {
    "Seasonal naive + growth": seasonal_naive,
    "Holt-Winters": holt_winters,
}


def mape(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean absolute percentage error, skipping months with zero sales."""
    actual, predicted = actual.to_numpy(), predicted.to_numpy()
    mask = actual != 0
    return float(np.mean(np.abs(actual[mask] - predicted[mask]) / actual[mask]) * 100)


def mae(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean absolute error in dollars."""
    return float(np.mean(np.abs(actual.to_numpy() - predicted.to_numpy())))


@dataclass
class ForecastResult:
    model: str
    backtest: pd.DataFrame  # one row per model: MAPE, MAE
    holdout: pd.DataFrame  # Month, Actual and one column per model
    history: pd.Series  # all monthly sales used for the final fit
    forecast: pd.DataFrame  # Month, Forecast, Lower, Upper


def run_forecast(df: pd.DataFrame, horizon: int = 6, holdout: int = 12) -> ForecastResult:
    """Backtest every model on the last ``holdout`` months, then forecast.

    Needs at least ``holdout + 24`` months of history so each model has two
    full seasons to learn from.
    """
    series = monthly_series(df)
    if len(series) < holdout + 2 * SEASON:
        raise ValueError(f"Need at least {holdout + 2 * SEASON} months of data, got {len(series)}.")
    empty_share = float((series == 0).mean())
    if empty_share > MAX_EMPTY_SHARE:
        raise ValueError(f"{empty_share:.0%} of months have no sales, too sparse to forecast.")

    train, test = series.iloc[:-holdout], series.iloc[-holdout:]
    holdout_table = pd.DataFrame({"Actual": test})
    rows = []
    for name, model in MODELS.items():
        predicted = model(train, holdout)
        predicted.index = test.index
        holdout_table[name] = predicted
        rows.append({"Model": name, "MAPE %": mape(test, predicted), "MAE $": mae(test, predicted)})
    backtest = pd.DataFrame(rows).sort_values("MAPE %").reset_index(drop=True)
    best = backtest.loc[0, "Model"]

    # Band width: typical dollar miss of the best model on the holdout
    spread = float((holdout_table["Actual"] - holdout_table[best]).std(ddof=1))

    point = MODELS[best](series, horizon)
    forecast = pd.DataFrame(
        {
            "Forecast": point,
            "Lower": np.clip(point - Z_80 * spread, 0, None),
            "Upper": point + Z_80 * spread,
        }
    )
    forecast.index.name = "Month"
    holdout_table.index.name = "Month"
    return ForecastResult(
        best, backtest, holdout_table.reset_index(), series, forecast.reset_index()
    )
